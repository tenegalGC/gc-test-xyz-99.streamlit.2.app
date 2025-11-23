import streamlit as st
import requests
from bs4 import BeautifulSoup
import qrcode
import pandas as pd
import io
import re

GC_LOGO = "https://www.gruppocorso.nl/media/logo/stores/1/logo_gruppo_corso.png"
PLACE_IMG = GC_LOGO

st.set_page_config(page_title="Gruppo Corso Zamówienia", page_icon="🛒", layout="centered")
st.markdown("""
    <style>
        .block-container { max-width: 560px !important; margin: auto; padding:0 1vw;}
        .main-title {font-size: 25px; color: #0A2444; text-align:center; font-weight:700; margin-bottom:15px;}
        #MainMenu, header, footer {visibility: hidden;}
        .custom-header { background: #fff; border-bottom:1px solid #eee; margin-bottom:16px;
          padding:16px 0 12px 0; display:flex; flex-direction:column; align-items:center;}
        .gc-logo {max-width: 120px;}
        label {font-weight:500;}
        .info-small {font-size:11px;color:#999;}
        .add-section {background:#fff; border-radius:10px; margin-bottom:20px; box-shadow:0 1px 14px #0002; padding:18px;}
        .carttable {width:100%; margin-bottom:14px;}
        .cart-th, .cart-td {padding:6px 8px; font-size:15px;}
        .cart-th {color:#0A2444; font-weight:700; background:#f7f7fa;}
        .cartrow {border-bottom:1px solid #eee;}
        .cart-img {height:48px; border-radius:4px; background:#eee;}
        .cart-del {font-size:23px; color:#fff; background:#e30613;border-radius:8px; border:none;padding:4px 14px 7px 14px; cursor:pointer;}
        .btn-gc {background: #EBAF3A; color:#fff; border:none; border-radius:5px; font-weight:700; font-size:15px; width:100%; margin:14px 0 8px 0; padding:15px 0;}
        .btn-gc:hover {background:#f7b202;}
        .qrbox {text-align:center; margin:12px auto;}
        .error-el {background: #fff6f6; color:#b20019; border:1px solid #fbb; margin-top:10px; padding: 9px 14px; border-radius:7px;}
    </style>
""", unsafe_allow_html=True)

if "prod_list" not in st.session_state:
    st.session_state.prod_list = []

# Layout:
st.markdown(f"""
<div class="custom-header">
    <img src="{GC_LOGO}" class="gc-logo"/>
    <div class="main-title">Zamówienia B2B Gruppo Corso</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="add-section">', unsafe_allow_html=True)
with st.form("Załaduj produkt po linku"):
    c1, c2 = st.columns([3,1])
    link = c1.text_input("Link do produktu", placeholder="https://www.gruppocorso.nl/...")
    qty = c2.number_input("Ilość", min_value=1, value=1, step=1)
    addok = st.form_submit_button("Dodaj ➕")
    if addok:
        if not link.startswith("http"):
            st.warning("Podaj prawidłowy link do produktu!")
        else:
            try:
                session = requests.Session()
                session.headers = {'User-Agent':'Mozilla/5.0'}
                r = session.get(link, timeout=7)
                soup = BeautifulSoup(r.text, "html.parser")
                pidelm = soup.find("input", {"name":"product"})
                if not pidelm:
                    st.warning("Nie znaleziono ID produktu na stronie. Upewnij się, że to link do DETALICZNEJ karty produktu!")
                else:
                    pid = pidelm["value"]
                    name = (soup.find("h1", {"class":"page-title"}).get_text(strip=True)
                               if soup.find("h1", {"class":"page-title"}) else link)
                    img = (soup.find("meta", {"property":"og:image"}).get("content")
                        if soup.find("meta", {"property":"og:image"}) else PLACE_IMG)
                    st.session_state.prod_list.append({"id":pid,"name":name,"qty":qty,"img":img,"link":link})
                    st.success("Dodano do koszyka.")
            except Exception as e:
                st.error("Błąd pobierania produktu. Ten link jest nieprawidłowy lub niedostępny.")
st.markdown('</div>', unsafe_allow_html=True)

# Cart Table (ładny, zawsze box)
if st.session_state.prod_list:
    st.markdown('<div style="font-size:20px;font-weight:700;margin:18px 0 8px 0;">Produkty w koszyku</div>', unsafe_allow_html=True)
    st.markdown('<table class="carttable"><tr class="cart-th"><td>Foto</td><td>Nazwa</td><td>Ilość</td><td>Usuń</td></tr>', unsafe_allow_html=True)
    for idx, p in enumerate(st.session_state.prod_list):
        st.markdown(
            f'<tr class="cartrow">'
            f'<td class="cart-td"><img src="{p["img"]}" class="cart-img"></td>'
            f'<td class="cart-td">{p["name"]}<br/><span class="info-small"><a href="{p["link"]}" target="_blank">{p["link"]}</a></span></td>'
            f'<td class="cart-td">{int(p["qty"])}</td>'
            f'<td class="cart-td"><form action="" method="post"><button class="cart-del" name="del_{idx}">🗑️</button></form></td>'
            f'</tr>', unsafe_allow_html=True)
        if st.session_state.get(f"del_{idx}", False):
            del st.session_state.prod_list[idx]
            st.experimental_rerun()
    st.markdown('</table>', unsafe_allow_html=True)
        
    # Generate button
    if st.button("🚀 GENERUJ LINK DO KOSZYKA I QR", type="primary"):
        with st.spinner("Tworzę koszyk..."):
            try:
                session = requests.Session()
                session.headers = {'User-Agent':'Mozilla/5.0'}
                r = session.get("https://www.gruppocorso.nl/checkout/cart/")
                fk = BeautifulSoup(r.text, "html.parser").find("input",{"name":"form_key"})["value"]
                for p in st.session_state.prod_list:
                    session.post(f"https://www.gruppocorso.nl/checkout/cart/add/product/{p['id']}/",
                        data={"product":p['id'],"qty":p['qty'],"form_key":fk})
                sr = session.get("https://www.gruppocorso.nl/sharecart/index/email/")
                mt = re.search(r'sharecart\/shared\/get\/id\/[^"]+', sr.text)
                if mt:
                    link = f"https://www.gruppocorso.nl/{mt.group(0)}".replace('"','')
                    st.success("Link wygenerowany!")
                    st.code(link)
                    qr = qrcode.make(link)
                    buf=io.BytesIO(); qr.save(buf); st.image(buf.getvalue(), width=180)
                else:
                    st.markdown('<div class="error-el">Błąd podczas generowania linku. Sprawdź, czy wszystkie produkty są dostępne.</div>', unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f'<div class="error-el">Błąd: {e}</div>', unsafe_allow_html=True)
    if st.button("🗑️ Opróżnij cały koszyk"):
        st.session_state.prod_list.clear()
        st.experimental_rerun()
else:
    st.info("Dodaj produkty przez link z karty produktu Gruppo Corso.")

st.markdown("<div style='height:60px'></div>", unsafe_allow_html=True)
