import streamlit as st
import random
import qrcode
import io

# Demo produkty (Mini-katalog kafelkowy)
PRODUCTS = [
    {"id": 1, "name": "Manekin sklepowy", "img": "https://placehold.co/70x70?text=Manekin", "price": 129.00},
    {"id": 2, "name": "Torso Męskie", "img": "https://placehold.co/70x70?text=Torso", "price": 89.00},
    {"id": 3, "name": "Wieszak metalowy", "img": "https://placehold.co/70x70?text=Wieszak", "price": 9.99},
    {"id": 4, "name": "Lampa sklepowa", "img": "https://placehold.co/70x70?text=Lampa", "price": 75.00},
    {"id": 5, "name": "Toonbank", "img": "https://placehold.co/70x70?text=Toonbank", "price": 499.00},
    {"id": 6, "name": "Półka szklana", "img": "https://placehold.co/70x70?text=Półka", "price": 110.50},
    {"id": 7, "name": "Regał na odzież", "img": "https://placehold.co/70x70?text=Regał", "price": 299.00},
    {"id": 8, "name": "Krzesło eventowe", "img": "https://placehold.co/70x70?text=Krzesło", "price": 35.00},
    {"id": 9, "name": "Stolik Cafe", "img": "https://placehold.co/70x70?text=Stolik", "price": 59.90},
    {"id":10, "name": "Lustro sklepowe", "img": "https://placehold.co/70x70?text=Lustro", "price": 145.00},
    {"id":11, "name": "Kosz promocyjny", "img": "https://placehold.co/70x70?text=Kosz", "price": 25.00},
    {"id":12, "name": "Ekspozytor akrylowy", "img": "https://placehold.co/70x70?text=Ekspozytor", "price": 17.90},
]

st.set_page_config(page_title="Gruppo Corso – Order Demo", page_icon="🛒", layout="wide")
st.markdown("""
    <style>
        body, .stApp {background: #e8ecf4;}
        .main-header {background:#131829;padding:14px 28px 13px 28px;margin-bottom:27px; border-radius:0 0 14px 14px;}
        .header-content {display:flex;align-items:center;}
        .header-logo {max-width:42px;margin-right:13px;}
        .header-title {color:#fff;font-size:23px;font-weight:600;letter-spacing:0.5px;}
        .catalog-col {background:#fff; border-radius:15px;padding:24px;min-width:340px;}
        .order-col {background:#f9fafc;border-radius:16px;padding:20px 18px 20px 22px; min-width:350px;border-left:3px solid #EBAF3A;}
        .product-item {background:#f5f7fa; border-radius:9px; padding:9px 10px;display:flex;align-items:center;margin-bottom:13px;}
        .prod-img-thumb {height:47px;width:47px;border-radius:7px;margin-right:15px;background:#eee;}
        .prod-name {font-weight:600;font-size:15px;color:#131829;}
        .buy-btn {margin-left:auto; background:#EBAF3A;color:#fff;font-weight:700;border:none; border-radius:7px;padding:9px 15px;}
        .buy-btn:hover {background:#ffb200;}
        .order-header {font-size:16px;font-weight:700;margin-bottom:10px;color:#0A2444;}
        .order-row {display:flex;align-items:center;margin-bottom:10px;}
        .order-img {height:36px;width:36px;border-radius:7px;margin-right:12px;}
        .order-remove-btn {background:#bb1436;color:#fff;font-size:21px;border:none;margin-left:9px;border-radius:7px;width:33px;height:33px;}
        .order-price {font-weight:600;margin-left:auto;}
        .qr-panel {background:#fff; border-radius:12px;padding:17px;text-align:center;}
    </style>
    <div class="main-header">
      <div class="header-content">
        <img class="header-logo" src="https://www.gruppocorso.nl/media/logo/stores/1/logo_gruppo_corso.png" alt="logo"/>
        <span class="header-title">Gruppo Corso – Order Management</span>
      </div>
    </div>
""", unsafe_allow_html=True)

if "order" not in st.session_state:     st.session_state.order = {}
if "next_qr" not in st.session_state:   st.session_state.next_qr = ""

# --- LEWA KOLUMN -- produkt gallery
cols = st.columns([2.7, 1])        # LEFT:catalog, RIGHT:order
with cols[0]:
    st.markdown('<div class="catalog-col">', unsafe_allow_html=True)
    st.markdown("<b>Product Catalog</b>", unsafe_allow_html=True)
    # Kafelki 3x4
    for i in range(0, len(PRODUCTS), 3):
        row = st.columns(3)
        for j, idx in enumerate(range(i, min(i+3, len(PRODUCTS)))):
            p = PRODUCTS[idx]
            with row[j]:
                st.markdown(
                    f'<div class="product-item">'
                    f'<img src="{p["img"]}" class="prod-img-thumb"/>'
                    f'<span class="prod-name">{p["name"]}</span>'
                    f'<form style="display:inline" action="" method="post">'
                    f'  <button class="buy-btn" name="add_{p["id"]}">Add</button>'
                    f'</form></div>', unsafe_allow_html=True)
                if st.session_state.get(f"add_{p['id']}", False):
                    # Dodaj 1 do koszyka
                    st.session_state.order[p["id"]] = st.session_state.order.get(p["id"], 0) + 1
                    st.experimental_rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- PRAWO: zamówienie
with cols[1]:
    st.markdown('<div class="order-col">', unsafe_allow_html=True)
    st.markdown('<span class="order-header">Current Order</span>', unsafe_allow_html=True)
    total = 0.0
    for pid, qty in st.session_state.order.items():
        prod = next((p for p in PRODUCTS if p["id"] == pid), None)
        if not prod: continue
        row = st.columns([1, 4, 2, 1])
        row[0].image(prod["img"], width=36)
        row[1].markdown(f'<span>{prod["name"]}</span>', unsafe_allow_html=True)
        row[2].markdown(f"Qty: <b>{qty}</b>", unsafe_allow_html=True)
        if row[3].button("✕", key=f"rem_{pid}"):
            del st.session_state.order[pid]
            st.experimental_rerun()
        total += prod["price"] * qty
    st.markdown("---")
    # QR panel
    st.markdown('<div class="qr-panel">', unsafe_allow_html=True)
    if st.button("Generate QR Code", key="qrbtn", type="primary", use_container_width=True):
        code = "ORDER-" + str(random.randint(1000,99999))
        st.session_state.next_qr = code
    if st.session_state.next_qr:
        qrimg = qrcode.make(st.session_state.next_qr)
        b = io.BytesIO()
        qrimg.save(b)
        st.image(b.getvalue(), width=140)
        st.write(f"QR for: {st.session_state.next_qr}")
    st.markdown(f"**Total:** <span style='font-size:19px;color:#0A2444;font-weight:900'>{total:.2f} zł</span>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

