import streamlit as st
import requests
from bs4 import BeautifulSoup
import qrcode
import pandas as pd
import io
import re

FALLBACK_IMG = "https://www.gruppocorso.nl/media/logo/stores/1/logo_gruppo_corso.png"
NAVY = "#0A2444"
ORANGE = "#EBAF3A"

st.set_page_config(page_title="Gruppo Corso Koszyk", page_icon="🛒", layout="centered")
st.markdown(f"""
    <style>
        .block-container {{max-width: 540px !important; margin: auto; background:#fff; padding:0 2vw;}}
        body, .stApp {{background: #fff !important; color:{NAVY};}}
        .custom-header {{
            padding-top:18px; padding-bottom:8px; display:flex; flex-direction:column; align-items:center; background:#fff;
            border-bottom:2px solid {NAVY};
        }}
        .gc-logo {{max-width: 110px; padding-bottom:0;margin-bottom: -10px;}}
        .main-title {{font-size: 26px; text-align:center; color:{NAVY}; font-weight:800; letter-spacing:0.03em;}}
        label {{color:{NAVY}; font-size:15px;font-weight:600;}}
        .add-section{{margin:22px 0 16px 0;padding: 22px 10px 18px 10px; background:#f8f9fb; border-radius:12px;box-shadow:0 2px 14px #15315918}} 
        .btn-gc{{background:{ORANGE};color:#fff;border:none;border-radius:6px; font-weight:700;font-size:15px;width:100%;margin:14px 0 8px 0;padding:13px 0}}
        .btn-gc:hover{{background:#FFB000;}}
        .cart-img{{height:54px;border-radius:4px;background:#eee;}}
        .carttable{{border-collapse:collapse;width:100%;}}
        .cart-th{{padding:6px 8px;font-size:15px;color:{NAVY};background:#eef2fa;font-weight:700;}}
        .cart-td{{font-size:15px;padding:7px 8px;vertical-align:middle;}}
        .cart-del{{background:#b00028;color:#fff;border:none;width:34px;height:34px;border-radius:7px;text-align:center;font-size:19px;line-height:31px}}
        .qrbox{{text-align:center;margin:12px auto;}}
    </style>
    <div class="custom-header">
        <img src="{FALLBACK_IMG}" class="gc-logo"/>
        <div class="main-title">Zamówienia Gruppo Corso</div>
    </div>
""", unsafe_allow_html=True)

if "prod_list" not in st.session_state:
    st.session_state.prod_list = []

# Pobranie danych po linku, zwraca: id, nazwa, obrazek (z fallbackiem na logo GC)
def get_product_from_link(link):
    try:
        session = requests.Session()
        session.headers = {'User-Agent':'Mozilla/5.0'}
        r = session.get(link, timeout=8)
        soup = BeautifulSoup(r.content, "html.parser")
        pidel = soup.find("input", {"name": "product"})
        if not pidel: return None,None,None
        pid = pidel["value"]
        name = soup.find("h1",{"class":"page-title"})
        name = name.get_text(strip=True) if name else link
        # Pobierz pierwszy duży obrazek produktu, lub fallback (logo)
        img = FALLBACK_IMG
        ogimg = soup.find("meta",{"property":"og:image"})
        if ogimg and ogimg.get("content") and "logo" not in ogimg.get("content"):
            img = ogimg["content"]
        else:
            imgtag = soup.find("img",{"class":"fotorama__img"}) or soup.find("img",{"class":"gallery-placeholder__image"})
            if imgtag and imgtag.get("src"): img = imgtag["src"]
        return pid, name, img
    except:
        return None,None,FALLBACK_IMG

st.markdown('<div class="add-section">', unsafe_allow_html=True)
with st.form("addprod"):
    c1, c2 = st.columns([3,1])
    link = c1.text_input("Link do produktu", placeholder="https://www.gruppocorso.nl/...")
    qty = c2.number_input("Ilość", min_value=1, value=1, step=1)
    addok = st.form_submit_button("Dodaj ➕")
    if addok:
        if not link.startswith("http"):
            st.warning("Podaj prawidłowy link do produktu (https...)!")
        else:
            pid, name, img = get_product_from_link(link)
            if not pid:
                st.warning("Nie znaleziono produktu po tym linku.")
            else:
                st.session_state.prod_list.append({"id": pid, "name": name, "img": img, "qty": qty, "link": link})

st.markdown('</div>', unsafe_allow_html=True)

# Koszyk (ładne kafelki na białym tle)
if st.session_state.prod_list:
    st.markdown('<table class="carttable"><tr class="cart-th"><td>Foto</td><td>Nazwa</td><td>Ilość</td><td>Usuń</td></tr>', unsafe_allow_html=True)
    for idx, p in enumerate(st.session_state.prod_list):
        st.markdown(
            f'<tr><td class="cart-td"><img src="{p["img"]}" class="cart-img"></td>'
            f'<td class="cart-td">{p["name"]}<br/><span style="font-size:11px;color:#888"><a href="{p["link"]}" target="_blank">{p["link"]}</a></span></td>'
            f'<td class="cart-td">{int(p["qty"])}</td>'
            f'<td class="cart-td"><form action="" method="post"><button class="cart-del" name="del_{idx}">✕</button></form></td>'
            '</tr>', unsafe_allow_html=True)
        # Usuwanie (hack na refresh: używaj tylko tego kodu lokalnie/na własność)
        if st.session_state.get(f"del_{idx}", False):
            del st.session_state.prod_list[idx]
            st.rerun()
    st.markdown('</table>', unsafe_allow_html=True)

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
                    st.success("Twój koszyk jest gotowy!")
                    st.code(link)
                    qr = qrcode.make(link)
                    buf = io.BytesIO()
                    qr.save(buf, format='PNG')
                    buf.seek(0)
                    st.image(buf, width=185)
                else:
                    st.error("Błąd podczas generowania linku. Sprawdź, czy wszystkie produkty są aktualnie dostępne na stronie.")
            except Exception as e:
                st.error(f"Błąd koszyka: {e}")
    if st.button("🗑️ Opróżnij koszyk"):
        st.session_state.prod_list.clear()
        st.rerun()
else:
    st.info("Dodaj produkt przez wklejenie linku powyżej.")


