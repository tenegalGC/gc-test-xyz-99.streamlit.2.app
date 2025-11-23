import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import qrcode
from PIL import Image
import io
import re

# --- BRANDING JAK GRUPPO CORSO ---
st.set_page_config(page_title="Gruppo Corso B2B Zamówienia", page_icon="🛒", layout="wide")
st.markdown("""
    <style>
        body {background: #f4f4f4;}
        .block-container {padding-top: 0;}
        #MainMenu, #main-menu {visibility: hidden;}
        footer {visibility: hidden;}
        .custom-header {
            background-color: white; border-bottom: 1px solid #eee; display: flex; align-items: center;
            padding: 13px 20px 13px 10px; margin-bottom:20px;
        }
        .logo {height: 41px;}
        .app-title {color: #0A2444; font-size: 21px; font-weight:700; margin-left:12px;}
        .btn-yellow button {
            background: #EBAF3A !important; color: #fff !important; font-weight: bold;
        }
        .btn-blue button {
            background: #0A2444 !important; color: #fff !important; font-weight: bold;
            border:none;
        }
        .stDataFrame img {border-radius:6px;}
        .stDataFrame {background: #fff;}
    </style>
    <div class="custom-header">
        <img src="https://www.gruppocorso.nl/media/logo/stores/1/logo_gruppo_corso.png" class="logo">
        <span class="app-title">Zamówienia B2B - Gruppo Corso</span>
    </div>
""", unsafe_allow_html=True)

if 'koszyk' not in st.session_state:
    st.session_state.koszyk = []

# --- Funkcja pobierania ID, nazwy i obrazka z linku ---
def get_product_info(url_or_id):
    session = requests.Session()
    session.headers = {'User-Agent': 'Mozilla/5.0'}
    if "http" not in url_or_id:
        return url_or_id, f"Produkt {url_or_id}", "https://placehold.co/60x60"
    try:
        r = session.get(url_or_id, timeout=6)
        if r.status_code != 200: return None, None, None
        soup = BeautifulSoup(r.text, 'html.parser')
        pid = soup.find("input", {"name": "product"})
        pid = pid["value"] if pid else None
        name = (soup.find("h1", {"class": "page-title"}).get_text(strip=True)
                if soup.find("h1", {"class": "page-title"}) else "Produkt")
        img = None
        img_meta = soup.find("meta", {"property": "og:image"})
        if img_meta:
            img = img_meta["content"]
        else:
            img = "https://placehold.co/60x60"
        return pid, name, img
    except:
        return None, None, None

# --- Funkcja generowania linku koszyka ---
def create_magento_cart(cart_items):
    session = requests.Session()
    session.headers = {'User-Agent': 'Mozilla/5.0'}
    base_url = "https://www.gruppocorso.nl"
    try:
        r = session.get(f"{base_url}/checkout/cart/")
        form_key = BeautifulSoup(r.text, 'html.parser').find("input", {"name": "form_key"})["value"]
        for item in cart_items:
            session.post(f"{base_url}/checkout/cart/add/product/{item['id']}/", 
                         data={"product": item['id'], "qty": item['qty'], "form_key": form_key})
        share_r = session.get(f"{base_url}/sharecart/index/email/")
        match = re.search(r'sharecart\/shared\/get\/id\/[^"]+', share_r.text)
        if match: return f"{base_url}/{match.group(0)}".replace('"', '')
        return None
    except: return None

# --- UI: Panel dodawania produktu ---
st.markdown("#### Dodaj produkt do zamówienia")
col1, col2 = st.columns([5, 2])
with col1:
    inp = st.text_input("Link do produktu / ID", placeholder="np. https://www.gruppocorso.nl/etalagepoppen/xyz", label_visibility="collapsed", key="prod_inp")
with col2:
    qty = st.number_input("Ilość", min_value=1, max_value=500, step=1, value=1, label_visibility="collapsed", key="qty_inp")

add_btn = st.button("Dodaj", key="add_btn", help="Dodaj produkt do zamówienia", use_container_width=True)

# --- Dodanie produktu do koszyka po kliknięciu ---
if add_btn and inp:
    with st.spinner("Pobieram dane produktu..."):
        pid, name, img_url = get_product_info(inp)
        if pid:
            st.session_state.koszyk.append({"img": img_url, "name": name, "id": pid, "qty": qty})
            st.success(f'Dodano: {name}')
            st.experimental_rerun()
        else:
            st.error("Nie udało się pobrać produktu. Sprawdź link lub ID!")

# --- TABELA ZAMÓWIENIA ---
if len(st.session_state.koszyk):
    st.markdown("#### Wybrany koszyk produktów")
    df = pd.DataFrame(st.session_state.koszyk)
    edited = st.data_editor(
        df,
        column_config={
            "img": st.column_config.ImageColumn("Zdjęcie", width="small"),
            "name": st.column_config.TextColumn("Nazwa", disabled=True),
            "id": st.column_config.TextColumn("ID", disabled=True),
            "qty": st.column_config.NumberColumn("Ilość", min_value=1, step=1)
        },
        hide_index=True,
        use_container_width=True,
        num_rows="dynamic"
    )
    
    st.markdown("---")
    if st.button("GEN-GRUPO LINK & QR", type="primary", use_container_width=True, key="btn_gen"):
        fin_items = edited.to_dict('records')
        with st.spinner("Generuję link do koszyka..."):
            link = create_magento_cart(fin_items)
            if link:
                st.success("Gotowe! Oto link dla klienta:")
                st.code(link)
                qr = qrcode.QRCode(box_size=7, border=2)
                qr.add_data(link)
                qr.make(fit=True)
                buf = io.BytesIO()
                qr.make_image(fill_color="black", back_color="white").save(buf)
                st.image(buf, width=200)
            else:
                st.error("Błąd podczas generowania linku do koszyka!")
    if st.button("🗑️ Wyczyść koszyk", use_container_width=True, key="btn_clear"):
        st.session_state.koszyk = []
        st.experimental_rerun()
else:
    st.info("Dodaj pierwszy produkt do zamówienia powyżej.")

### 2. Przygotuj `requirements.txt` (do GitHub repo):


