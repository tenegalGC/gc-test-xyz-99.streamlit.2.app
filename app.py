import random
import string
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

# ============================================================
# KONFIGURACJA
# ============================================================
APP_DIR = Path(__file__).parent
ASSETS = APP_DIR / "assets"
DATA_DIR = APP_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
ORDERS_FILE = DATA_DIR / "orders.csv"

# Uzupełnij własnymi linkami, gdy będą gotowe – jeśli puste, ikonki pokażą się bez linku.
INSTAGRAM_URL = ""
TIKTOK_URL = ""

# Hasło do panelu sprzedawcy – najlepiej ustawić przez st.secrets["admin_password"].
try:
    ADMIN_PASSWORD = st.secrets.get("admin_password", "cozybox2025")
except Exception:
    ADMIN_PASSWORD = "cozybox2025"

SHIPPING_COST = 19.00

BOX_TYPES = {
    "cozy": {
        "name": "Cozy Box",
        "price": 70.00,
        "tagline": "Mini Scoop + 1 losowy prezent",
        "img": "gallery_1.jpg",
        "includes": [
            "1 Mini Scoop – minimum 15 kolorowych koralików",
            "1 losowy prezent (m.in. kosmetyczka, zestaw maseczek, lip care set, koreański krem do rąk, puchaty notes...)",
            "Kilka drobnych gratisów dobranych osobiście przez Kim",
        ],
    },
    "kpop": {
        "name": "K-Pop Cozy Box",
        "price": 99.00,
        "tagline": "Mini Scoop + losowy prezent K-pop + karta GRATIS",
        "img": "gallery_3.jpg",
        "includes": [
            "1 Mini Scoop – minimum 15 kolorowych koralików",
            "1 losowy prezent K-pop (album SEVENTEEN / ATEEZ / WONHO / GOT7 lub kubek BT21)",
            "Dodatkowa karta K-pop GRATIS",
            "Kilka drobnych gratisów dobranych osobiście przez Kim",
        ],
    },
}

GIFT_POOL = [
    "Piórnik / kosmetyczka",
    "Zestaw maseczek",
    "Biurowy set",
    "Lip care set",
    "Opaska do makijażu / skincare",
    "Ampułki Babor",
    "Koreańskie kremy do rąk",
    "Notesy większe / puchate",
]

KPOP_GIFT_POOL = [
    "Album SEVENTEEN",
    "Album ATEEZ",
    "Album WONHO",
    "Album GOT7",
    "Kubek BT21",
]

DELIVERY_OPTIONS = {
    "paczkomat": "Paczkomat → Paczkomat",
    "dom": "Paczkomat → Dom (kurier)",
}

PAYMENT_OPTIONS = ["BLIK", "Przelew bankowy"]

ORDER_COLUMNS = [
    "order_id", "timestamp", "items", "subtotal", "shipping", "total",
    "delivery_method", "delivery_details", "name", "phone", "contact",
    "payment_method", "notes", "status",
]

STATUS_OPTIONS = ["Nowe", "Opłacone", "Wysłane", "Zrealizowane", "Anulowane"]


def img(name: str) -> str:
    return str(ASSETS / name)


# ============================================================
# POMOCNICZE FUNKCJE
# ============================================================
def load_orders() -> pd.DataFrame:
    if ORDERS_FILE.exists():
        try:
            return pd.read_csv(ORDERS_FILE, dtype=str).fillna("")
        except Exception:
            pass
    return pd.DataFrame(columns=ORDER_COLUMNS)


def save_orders(df: pd.DataFrame) -> None:
    df.to_csv(ORDERS_FILE, index=False)


def new_order_id() -> str:
    stamp = datetime.now().strftime("%y%m%d")
    suffix = "".join(random.choices(string.digits, k=4))
    return f"CB-{stamp}-{suffix}"


def cart_lines():
    lines = []
    for key, qty in st.session_state.cart.items():
        if qty > 0:
            lines.append((key, qty))
    return lines


def cart_subtotal() -> float:
    return sum(BOX_TYPES[key]["price"] * qty for key, qty in cart_lines())


# ============================================================
# STYL / CSS
# ============================================================
st.set_page_config(page_title="Cozy Box by Kim", page_icon="🎀", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Caveat:wght@600;700&family=Quicksand:wght@400;500;600;700&display=swap');

html, body, .stApp {
    background: #fdf1f4;
    font-family: 'Quicksand', sans-serif;
    color: #5c4033;
}
h1, h2, h3 { font-family: 'Quicksand', sans-serif; color: #5c4033; }

.cozy-script {
    font-family: 'Caveat', cursive;
    color: #d6577c;
    font-weight: 700;
}

.hero-wrap {
    border-radius: 22px;
    overflow: hidden;
    border: 2px solid #f3c6d3;
    margin-bottom: 22px;
}

.tagline-badge {
    display: inline-block;
    background: linear-gradient(90deg, #f7c9d9, #d8bdf0);
    color: #5c4033;
    font-weight: 700;
    padding: 4px 16px;
    border-radius: 999px;
    margin: 6px 4px;
    font-size: 0.9rem;
}

.cozy-card {
    background: #fffaf9;
    border: 2px dashed #f0aec3;
    border-radius: 18px;
    padding: 22px 24px;
    margin-bottom: 18px;
}

.price-card {
    background: #ffffff;
    border: 2px solid #f3c6d3;
    border-radius: 20px;
    padding: 24px;
    text-align: center;
    height: 100%;
}
.price-card h2 { color: #d6577c; margin-bottom: 0; }
.price-card .price { font-size: 2.2rem; font-weight: 700; color: #5c4033; margin: 6px 0 2px 0; }
.price-card .tag { color: #8a6a9a; font-weight: 600; margin-bottom: 10px; }

.gift-pill {
    display: inline-block;
    background: #fbe4ea;
    color: #5c4033;
    border-radius: 12px;
    padding: 6px 12px;
    margin: 4px;
    font-size: 0.88rem;
    font-weight: 600;
}
.gift-pill.kpop { background: #ece0fa; }

.section-title {
    font-family: 'Caveat', cursive;
    font-size: 2.4rem;
    color: #d6577c;
    margin-bottom: 0;
}
.section-sub {
    display: inline-block;
    background: #ece0fa;
    color: #5c4033;
    padding: 3px 14px;
    border-radius: 999px;
    font-weight: 600;
    margin-bottom: 14px;
}

.footer-note {
    text-align: center;
    color: #8a6a9a;
    margin-top: 30px;
    padding: 14px;
    font-family: 'Caveat', cursive;
    font-size: 1.4rem;
}

div.stButton > button {
    background: #EBAF3A;
    background: linear-gradient(90deg, #f2a4bd, #d6577c);
    color: white;
    font-weight: 700;
    border: none;
    border-radius: 10px;
    padding: 8px 18px;
}
div.stButton > button:hover {
    background: linear-gradient(90deg, #d6577c, #c04568);
    color: white;
}

.stTabs [data-baseweb="tab-list"] { gap: 6px; }
.stTabs [data-baseweb="tab"] {
    background-color: #fff0f4;
    border-radius: 12px 12px 0 0;
    padding: 8px 16px;
    font-weight: 600;
}
.stTabs [aria-selected="true"] {
    background-color: #f2a4bd !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE
# ============================================================
if "cart" not in st.session_state:
    st.session_state.cart = {key: 0 for key in BOX_TYPES}
if "last_order" not in st.session_state:
    st.session_state.last_order = None


# ============================================================
# NAGŁÓWEK / HERO
# ============================================================
col_logo, col_title = st.columns([1, 5])
with col_logo:
    st.image(img("logo.jpg"), use_container_width=True)
with col_title:
    st.markdown(
        """
        <div style="padding-top:10px;">
            <span class="cozy-script" style="font-size:3rem;">Cozy Box <span style="color:#5c4033;font-family:'Quicksand';">by Kim</span></span><br/>
            <span class="tagline-badge">little things, big joy 💗</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown('<div class="hero-wrap">', unsafe_allow_html=True)
st.image(img("banner.jpg"), use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

tabs = st.tabs([
    "🏠 Strona główna", "💗 Cennik", "🛍️ Zamów", "🚚 Wysyłka i płatność", "🔐 Panel sprzedawcy",
])

# ============================================================
# TAB 1 — STRONA GŁÓWNA
# ============================================================
with tabs[0]:
    c1, c2 = st.columns([1.2, 1])
    with c1:
        st.markdown('<p class="section-title">Poznaj Cozy Box by Kim</p>', unsafe_allow_html=True)
        st.markdown('<span class="section-sub">little things, big joy 💜</span>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="cozy-card">
            Cozy Box to pudełko pełne małych przyjemności i odrobiny niespodzianki. ✨<br/><br/>
            Nie wybierasz dokładnej zawartości – <b>to losowanie decyduje</b>, co znajdzie się
            w Twoim boxie!
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.image(img("gallery_1.jpg"), use_container_width=True)

    st.markdown("### 🌸 Na czym polega Mini Scoop?")
    m1, m2 = st.columns([1, 1])
    with m1:
        st.markdown(
            """
            <div class="cozy-card">
            Każdy Mini Box powstaje z <b>1 losowej łyżeczki kolorowych koralików</b>.<br/><br/>
            🥄 1 łyżeczka = minimum <b>15 koralików</b> + 🎁 1 losowy prezent<br/><br/>
            Każdy koralik odpowiada konkretnemu produktowi. To, co znajdzie się na łyżeczce,
            trafia do Twojego Cozy Boxa. <b>Im więcej koralików nabierze łyżeczka, tym więcej
            produktów znajdzie się w środku.</b><br/><br/>
            Prezent jest dodatkową niespodzianką i również wybierany jest losowo. 🎁
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m2:
        s1, s2 = st.columns(2)
        with s1:
            st.image(img("scoop_1.jpg"), use_container_width=True, caption="Koreański krem do rąk")
        with s2:
            st.image(img("scoop_2.jpg"), use_container_width=True, caption="Album SEVENTEEN")

    st.markdown("### 🌷 Zaczynamy od małych rzeczy...")
    z1, z2 = st.columns([1.3, 1])
    with z1:
        st.markdown(
            """
            <div class="cozy-card">
            Cozy Box by Kim to na razie <b>mały, rozwijający się projekt</b>, dlatego zaczynamy
            od Mini Scoopów. 🌸<br/><br/>
            💗 Małe pudełko<br/>
            💗 Mnóstwo drobiazgów<br/>
            💗 Za każdym razem inna niespodzianka<br/><br/>
            A z czasem? Kto wie, jak duży urośnie Cozy Box... 👀<br/><br/>
            Każdy Cozy Box pakuję ręcznie z dbałością o najmniejsze szczegóły. 💕
            </div>
            """,
            unsafe_allow_html=True,
        )
    with z2:
        st.image(img("gallery_4.jpg"), use_container_width=True)

    st.markdown("### 📸 Przykładowe Cozy Boxy")
    g1, g2, g3 = st.columns(3)
    with g1:
        st.image(img("gallery_1.jpg"), use_container_width=True)
    with g2:
        st.image(img("gallery_2.jpg"), use_container_width=True)
    with g3:
        st.image(img("gallery_3.jpg"), use_container_width=True)

# ============================================================
# TAB 2 — CENNIK
# ============================================================
with tabs[1]:
    st.markdown('<p class="section-title">Cennik</p>', unsafe_allow_html=True)
    st.write(
        "Mini Scoop, mnóstwo drobiazgów i jedna wielka niespodzianka! ✨ "
        "Każdy box to wyjątkowa kombinacja wybrana losowo specjalnie dla Ciebie."
    )

    p1, p2 = st.columns(2)
    with p1:
        b = BOX_TYPES["cozy"]
        st.markdown(
            f"""
            <div class="price-card">
              <h2>🌸 {b['name']}</h2>
              <div class="price">{b['price']:.0f} zł</div>
              <div class="tag">{b['tagline']}</div>
              <ul style="text-align:left;">
                {''.join(f'<li>{item}</li>' for item in b['includes'])}
              </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with p2:
        b = BOX_TYPES["kpop"]
        st.markdown(
            f"""
            <div class="price-card">
              <h2>💜 {b['name']}</h2>
              <div class="price">{b['price']:.0f} zł</div>
              <div class="tag">{b['tagline']}</div>
              <ul style="text-align:left;">
                {''.join(f'<li>{item}</li>' for item in b['includes'])}
              </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("")
    g1, g2 = st.columns(2)
    with g1:
        st.markdown("#### 🎁 Losowy prezent")
        st.markdown("".join(f'<span class="gift-pill">{g}</span>' for g in GIFT_POOL), unsafe_allow_html=True)
        st.caption("Pula prezentów będzie się stale zmieniać i powiększać! W przyszłości mogą pojawić się "
                   "również m.in. biżuteria, torebeczki, perfumy czy produkty do makijażu. ✨")
    with g2:
        st.markdown("#### 💜 K-Pop prezent")
        st.markdown("".join(f'<span class="gift-pill kpop">{g}</span>' for g in KPOP_GIFT_POOL), unsafe_allow_html=True)
        st.caption("Albumy są w idealnym stanie i zawierają wszystkie oryginalne dodatki znajdujące się w albumie. ✨")

    st.markdown(
        """
        <div class="cozy-card">
        <b>I jeszcze coś ode mnie... 💕</b><br/><br/>
        Do każdego Cozy Boxa dokładam kilka drobnych gratisów, które dobieram osobiście.
        Dbam o to, żeby żadna paczuszka nie była "poszkodowana" – dokładam wszelkich starań,
        aby każdy box sprawiał frajdę już od momentu otwarcia. ✨
        </div>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# TAB 3 — ZAMÓW
# ============================================================
with tabs[2]:
    st.markdown('<p class="section-title">Zamów Cozy Box</p>', unsafe_allow_html=True)
    st.write("Wybierz box, dodaj do zamówienia i uzupełnij dane do wysyłki. 💌")

    col_a, col_b = st.columns(2)
    for col, key in zip((col_a, col_b), BOX_TYPES):
        b = BOX_TYPES[key]
        with col:
            st.image(img(b["img"]), use_container_width=True)
            st.markdown(f"**{b['name']} — {b['price']:.0f} zł**")
            st.caption(b["tagline"])
            qty = st.number_input(
                f"Ilość — {b['name']}", min_value=0, max_value=10, value=0, step=1, key=f"qty_{key}",
            )
            if st.button(f"➕ Dodaj {b['name']} do zamówienia", key=f"add_{key}"):
                if qty > 0:
                    st.session_state.cart[key] = st.session_state.cart.get(key, 0) + int(qty)
                    st.success(f"Dodano {int(qty)} × {b['name']} do zamówienia.")
                else:
                    st.warning("Ustaw ilość większą niż 0.")

    st.divider()
    st.markdown("### 🧺 Twoje zamówienie")

    lines = cart_lines()
    if not lines:
        st.info("Twoje zamówienie jest puste — dodaj Cozy Box powyżej. 🌸")
    else:
        for key, qty in lines:
            b = BOX_TYPES[key]
            r1, r2, r3, r4 = st.columns([3, 1, 2, 1])
            r1.write(f"**{b['name']}**")
            r2.write(f"× {qty}")
            r3.write(f"{b['price'] * qty:.2f} zł")
            if r4.button("✕", key=f"rm_{key}"):
                st.session_state.cart[key] = 0
                st.rerun()

        subtotal = cart_subtotal()
        st.markdown(f"Wartość produktów: **{subtotal:.2f} zł**")
        st.markdown(f"Wysyłka (stała cena): **{SHIPPING_COST:.2f} zł**")
        st.markdown(f"### Razem: **{subtotal + SHIPPING_COST:.2f} zł**")

        st.markdown("#### 🚚 Dostawa")
        delivery_key = st.radio(
            "Forma dostawy", list(DELIVERY_OPTIONS.keys()),
            format_func=lambda k: DELIVERY_OPTIONS[k], horizontal=True,
        )
        if delivery_key == "paczkomat":
            paczkomat_code = st.text_input("Numer / adres Paczkomatu odbiorcy (np. WAW01A)")
            delivery_details = f"Paczkomat: {paczkomat_code}"
        else:
            addr_col1, addr_col2 = st.columns(2)
            street = addr_col1.text_input("Ulica i numer domu/mieszkania")
            city = addr_col2.text_input("Miasto")
            postal = st.text_input("Kod pocztowy")
            delivery_details = f"Adres: {street}, {postal} {city}"

        st.markdown("#### 📇 Dane kontaktowe")
        c1, c2 = st.columns(2)
        name = c1.text_input("Imię i nazwisko")
        phone = c2.text_input("Telefon")
        contact = st.text_input("E-mail lub Instagram/TikTok (do kontaktu ws. zamówienia)")

        st.markdown("#### 💳 Płatność")
        payment_method = st.radio("Wybierz metodę płatności", PAYMENT_OPTIONS, horizontal=True)
        st.caption(
            "Płatność przyjmuję na ten moment przez wiadomość prywatną. Po złożeniu zamówienia "
            "napisz do mnie na Instagramie lub TikToku podając numer zamówienia — prześlę dane do płatności."
        )

        notes = st.text_area(
            "Uwagi do zamówienia (opcjonalnie)",
            placeholder="np. ulubiona grupa K-pop, alergie na kosmetyki, życzenia specjalne...",
        )

        agree = st.checkbox(
            "Rozumiem, że zawartość Cozy Boxa jest losowa i akceptuję zasady zamówienia. 💗"
        )

        if st.button("💌 Złóż zamówienie", type="primary"):
            missing = []
            if not name:
                missing.append("imię i nazwisko")
            if not phone:
                missing.append("telefon")
            if not contact:
                missing.append("e-mail lub Instagram/TikTok")
            if delivery_key == "paczkomat" and not paczkomat_code:
                missing.append("numer Paczkomatu")
            if delivery_key == "dom" and (not street or not city or not postal):
                missing.append("pełny adres dostawy")
            if not agree:
                missing.append("akceptację zasad zamówienia")

            if missing:
                st.error("Uzupełnij: " + ", ".join(missing))
            else:
                order_id = new_order_id()
                items_str = "; ".join(
                    f"{BOX_TYPES[k]['name']} x{q}" for k, q in lines
                )
                order_row = {
                    "order_id": order_id,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "items": items_str,
                    "subtotal": f"{subtotal:.2f}",
                    "shipping": f"{SHIPPING_COST:.2f}",
                    "total": f"{subtotal + SHIPPING_COST:.2f}",
                    "delivery_method": DELIVERY_OPTIONS[delivery_key],
                    "delivery_details": delivery_details,
                    "name": name,
                    "phone": phone,
                    "contact": contact,
                    "payment_method": payment_method,
                    "notes": notes,
                    "status": "Nowe",
                }
                df = load_orders()
                df = pd.concat([df, pd.DataFrame([order_row])], ignore_index=True)
                save_orders(df)

                st.session_state.last_order = order_row
                st.session_state.cart = {key: 0 for key in BOX_TYPES}
                st.rerun()

    if st.session_state.last_order:
        o = st.session_state.last_order
        st.success(f"Zamówienie **{o['order_id']}** zostało zapisane! 🎉")
        st.markdown("Skopiuj poniższą wiadomość i wyślij ją do mnie na Instagramie lub TikToku, "
                     "abym mogła przesłać dane do płatności:")
        summary = (
            f"Cześć! Składam zamówienie {o['order_id']} w Cozy Box by Kim.\n"
            f"Produkty: {o['items']}\n"
            f"Dostawa: {o['delivery_method']} — {o['delivery_details']}\n"
            f"Płatność: {o['payment_method']}\n"
            f"Razem do zapłaty: {o['total']} zł\n"
            f"Dane kontaktowe: {o['name']}, tel. {o['phone']}, {o['contact']}"
        )
        st.code(summary, language=None)
        icons = []
        if INSTAGRAM_URL:
            icons.append(f"[📷 Instagram]({INSTAGRAM_URL})")
        if TIKTOK_URL:
            icons.append(f"[🎵 TikTok]({TIKTOK_URL})")
        if icons:
            st.markdown(" &nbsp; ".join(icons))

# ============================================================
# TAB 4 — WYSYŁKA I PŁATNOŚĆ
# ============================================================
with tabs[3]:
    st.markdown('<p class="section-title">Wysyłka i płatność</p>', unsafe_allow_html=True)

    w1, w2 = st.columns(2)
    with w1:
        st.markdown(
            f"""
            <div class="cozy-card">
            <h4>📦 Wysyłka — {SHIPPING_COST:.0f} zł</h4>
            Stała cena wysyłki, niezależnie od wybranej formy dostawy.<br/><br/>
            Do wyboru:<br/>
            💗 {DELIVERY_OPTIONS['paczkomat']}<br/>
            💗 {DELIVERY_OPTIONS['dom']}<br/><br/>
            Każdy Cozy Box jest starannie zabezpieczony i pakowany przeze mnie. 🎀
            </div>
            """,
            unsafe_allow_html=True,
        )
    with w2:
        st.markdown(
            """
            <div class="cozy-card">
            <h4>💳 Płatność</h4>
            Na ten moment zamówienia przyjmuję przez <b>wiadomość prywatną</b>.<br/><br/>
            💗 BLIK<br/>
            💗 Przelew bankowy<br/><br/>
            Po ustaleniu szczegółów zamówienia przesyłam dane do płatności.
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div class="cozy-card">
        <h4>✨ Co dalej?</h4>
        Cozy Box by Kim to na razie mały, rozwijający się projekt. W przyszłości planuję
        uruchomienie strony internetowej z pełnymi płatnościami online, dzięki której zamawianie
        będzie jeszcze prostsze i wygodniejsze dla Was — a Ty właśnie z niej korzystasz! 🎀
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### 📩 Kontakt")
    contact_bits = ["Napisz do mnie na Instagramie lub TikToku, aby dograć szczegóły zamówienia i płatność. 💌"]
    st.write(" ".join(contact_bits))
    icons = []
    if INSTAGRAM_URL:
        icons.append(f"[📷 Instagram]({INSTAGRAM_URL})")
    if TIKTOK_URL:
        icons.append(f"[🎵 TikTok]({TIKTOK_URL})")
    if icons:
        st.markdown(" &nbsp; ".join(icons))
    else:
        st.caption("(Linki do social media pojawią się tutaj — uzupełnij INSTAGRAM_URL / TIKTOK_URL w app.py)")

# ============================================================
# TAB 5 — PANEL SPRZEDAWCY
# ============================================================
with tabs[4]:
    st.markdown('<p class="section-title">Panel sprzedawcy</p>', unsafe_allow_html=True)
    pwd = st.text_input("Hasło dostępu", type="password")
    if pwd != ADMIN_PASSWORD:
        if pwd:
            st.error("Nieprawidłowe hasło.")
        st.info("Podaj hasło, aby zobaczyć złożone zamówienia.")
    else:
        df = load_orders()
        if df.empty:
            st.info("Brak zamówień.")
        else:
            total_revenue = pd.to_numeric(df["total"], errors="coerce").sum()
            m1, m2 = st.columns(2)
            m1.metric("Liczba zamówień", len(df))
            m2.metric("Suma wartości zamówień", f"{total_revenue:.2f} zł")

            edited = st.data_editor(
                df,
                column_config={
                    "status": st.column_config.SelectboxColumn("status", options=STATUS_OPTIONS),
                },
                disabled=[c for c in ORDER_COLUMNS if c != "status"],
                use_container_width=True,
                hide_index=True,
                key="orders_editor",
            )
            if st.button("💾 Zapisz zmiany statusów"):
                save_orders(edited)
                st.success("Zapisano.")

            st.download_button(
                "⬇️ Pobierz zamówienia (CSV)",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="cozy_box_zamowienia.csv",
                mime="text/csv",
            )

st.markdown(
    '<div class="footer-note">Cozy Box by Kim — little things, big joy 💗</div>',
    unsafe_allow_html=True,
)
