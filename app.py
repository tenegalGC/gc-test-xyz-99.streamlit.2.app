import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import qrcode
from PIL import Image
import io
import re

# -- BRANDING/STYL GC --
st.set_page_config(page_title="Gruppo Corso Generator", page_icon="🛒", layout="centered")
st.markdown("""
    <style>
        .block-container {padding-top:0;}
        #MainMenu, header, footer {visibility: hidden;}
        body, .stApp {background: #f4f4f4;}
        .custom-header {
            margin-top:0px; margin-bottom:25px; display: flex; flex-direction:column; align-items: center;
        }
        .gc-logo {width: 120px;}
        .main-title {font-size: 28px; color: #0a2444; font-weight: bold; margin-top: 16px; text-align:center;}
        .add-section {background:#fff; border-radius:8px; margin-bottom:20px; box-shadow:0 1px 10px #0001; padding:20px;}
        .btn-gc {background: #EBAF3A !important; color:#fff !important; border:none; border-radius:5px; font-weight:600;}
        .big-btn {font-size:16px !important; width:100% !important;}
        .rm-btn {color: #fff !important; background: #b00028 !important; border:none;}
        table, .stDataFrame {background:#fff !important;}
        td, th {font-size:15px;}
        @media (max-width:800px) { .main-title{font-size:20px;} }
    </style>
    <div class="custom-header">
        <img src="https://www.gruppocorso.nl/media/logo/stores/1/logo_gruppo_corso.png" class="gc-logo"/>
        <div class="main-title">Generator Koszyków B2B dla Gruppo Corso</div>
    </div>
""", unsafe_allow_html=True)

# --- KOSZYK jako zmienna sesyjna (trwała) ---
if 'products' not in st.session_state:
    st.session_state.products = []

# --- Pobieranie danych produktu tylko z linku ---
def get_product_from_link(link):
    try:
        session = requests.Session()
        session.headers = {'User-Agent': 'Mozilla/5.0'}
        r = session.get(link, timeout=8)
        soup = BeautifulSoup(r.content, "html.parser")
        pid_input = soup.find("input", {"name": "product"})
        if not pid_input:
            return None, None, None
        pid = pid_input["value"]
        name = soup.find("h1", {"class": "page-title"})
        name = name.get_text(strip=True) if name else "Produkt (brak nazwy)"
        img = soup.find("meta", {"property":"og:image"})
        img = img["content"] if img and img.has_attr("content") else "https://www.gruppocorso.nl/media/logo/stores/1/logo_gruppo_corso.png"
        return pid, name, img
    except:
        return None, None, "https://www.gruppocorso.nl/media/logo/stores/1/logo_gruppo_corso.png"

# --- DODAWANIE PRODUKTÓW ---
st.markdown('<div class="add-section">', unsafe_allow_html=True)
with st.form("add-prod"):
    c1, c2, c3 = st.columns([4,2,1])
    with c1:
        link = st.text_input("Link do produktu ze strony Gruppo Corso", key="prod_url",
                             placeholder="https://www.gruppocorso.nl/nazwa-produktu")
    with c2:
        qty = st.number_input("Ilość", min_value=1, max_value=250, value=1, key="prod_qty")
    with c3:
        st.markdown(" ")
        add_btn = st.form_submit_button("Dodaj ➕", use_container_width=True)
    st.caption("**Wklej TYLKO link do produktu, np. ze strony wyszukiwania lub listingu.**")

st.markdown('</div>', unsafe_allow_html=True)

if add_btn:
    if not link.startswith("http"):
        st.error("Proszę podać prawidłowy link (https...)!")
    else:
        with st.spinner("Pobieram dane produktu..."):
            pid, name, image = get_product_from_link(link)
            if not pid:
                st.error("Nie udało się znaleźć tego produktu po linku.")
            else:
                st.session_state.products.append(
                    {"pid": pid, "sku": link, "name": name, "qty": int(qty), "img": image}
                )
                st.success(f"Dodano do koszyka: {name}")

# --- WYŚWIETLANIE KOSZYKA (edycja i usuwanie) ---
if st.session_state.products:
    st.markdown("### Produkty w koszyku")
    # tabelka headery
    cols_t = st.columns([1.3, 4, 2, 1])
    cols_t[0].markdown("**Foto**")
    cols_t[1].markdown("**Nazwa produktu**")
    cols_t[2].markdown("**Ilość**")
    cols_t[3].markdown("**Usuń**")
    # produkty: po jednym wierszu (ładna lista)
    for idx, prod in enumerate(st.session_state.products):
        cols = st.columns([1.3, 4, 2, 1])
        cols[0].image(prod['img'], width=56)
        cols[1].markdown(f"{prod['name']}<br/><span style='font-size:11px;color:#888'>{prod['sku']}</span>", unsafe_allow_html=True)
        prod['qty'] = cols[2].number_input(
            f"Ilość_{idx}", min_value=1, max_value=250, value=prod['qty'],
            key=f"q_{idx}"
        )
        if cols[3].button("🗑️", key=f"del_{idx}", help="Usuń produkt", type="primary"):
            st.session_state.products.pop(idx)
            st.experimental_rerun()

    st.markdown("---")
    if st.button("🚀 GENERUJ LINK DO KOSZYKA i QR", type="primary", use_container_width=True):
        # budowanie koszyka na bazie PID (Magento nie używa SKU/Link tylko PID do add-to-cart)
        with st.spinner("Tworzę link..."):
            session = requests.Session()
            session.headers = {'User-Agent': 'Mozilla/5.0'}
            base_url = "https://www.gruppocorso.nl"
            response = session.get(f"{base_url}/checkout/cart/")
            form_key = BeautifulSoup(response.text, 'html.parser').find("input", {"name": "form_key"})["value"]
            for p in st.session_state.products:
                session.post(f"{base_url}/checkout/cart/add/product/{p['pid']}/",
                             data={"product": p['pid'], "qty": p['qty'], "form_key": form_key})
            share_r = session.get(f"{base_url}/sharecart/index/email/")
            match = re.search(r'sharecart\/shared\/get\/id\/[^"]+', share_r.text)
            if match:
                link = f"{base_url}/{match.group(0)}".replace('"', '')
                st.success("Twój koszyk jest gotowy! Oto link dla klienta:")
                st.code(link)
                qr = qrcode.make(link)
                buf = io.BytesIO()
                qr.save(buf, format="PNG")
                st.image(buf, width=190)
            else:
                st.error("Błąd podczas generowania linku do koszyka. Sprawdź, czy wszystkie produkty są dostępne na stronie.")

    if st.button("🗑️ Opróżnij cały koszyk"):
        st.session_state.products.clear()
        st.experimental_rerun()
else:
    st.info("Dodaj produkty przez wklejenie linków powyżej.")
