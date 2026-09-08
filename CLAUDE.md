# Cozy Box by Kim — notatki projektowe

Aplikacja Streamlit do zamawiania lucky boxów (`app.py`, ~680 linii).
Deploy: Streamlit Community Cloud, automatycznie po pushu do `main`.

## Uruchomienie lokalne

```bash
pip install -r requirements.txt
streamlit run app.py --server.port 8501 --server.headless true
```

Panel sprzedawcy: hasło z `st.secrets["admin_password"]`, fallback w kodzie.
Sekrety trzymamy w `.streamlit/secrets.toml` (w `.gitignore`, nigdy do repo).

---

## ⚠️ DO ZROBIENIA PRZED PRODUKCJĄ — trwałość zamówień

**Przypomnij o tym na początku pracy nad tym projektem.**

Zamówienia zapisują się wyłącznie do pliku `data/orders.csv`
(`load_orders()` / `save_orders()`, app.py:97-107). Ten plik jest w `.gitignore`,
a dysk na Streamlit Community Cloud jest **ulotny** — kontener restartuje się
przy każdym deployu, po zmianie w repo i po okresie bezczynności.

Skutek: **po restarcie wszystkie zamówienia znikają bezpowrotnie.**
Nie ma żadnego backupu poza ręcznym „⬇️ Pobierz zamówienia (CSV)" w panelu
sprzedawcy (app.py:673) — a żeby go kliknąć, trzeba zdążyć przed restartem.

Dopóki to nie jest naprawione, apka nadaje się tylko do demo/testów, nie do
przyjmowania prawdziwych zamówień.

### Proponowane rozwiązanie

Przenieść zapis do Google Sheets jako bazy danych — zgodnie z konwencją
Gruppo Corso (skill `gruppocorso-apps-script`: arkusz jako baza, sekrety
w PropertiesService / `st.secrets`, powiadomienia na it@gruppocorso.nl).

Zakres zmiany jest mały i dobrze odizolowany — wystarczy podmienić dwie
funkcje, reszta aplikacji operuje na `DataFrame` i nie musi się zmieniać:

- `load_orders()` — czyta z arkusza zamiast z CSV
- `save_orders(df)` — zapisuje do arkusza zamiast do CSV

Do tego: service account w `st.secrets`, `gspread` w `requirements.txt`
i opcjonalnie mail na it@gruppocorso.nl przy nowym zamówieniu.

Alternatywa (szybsza, ale słabsza): natywne połączenie Streamlit
`st.connection("gsheets")`.

---

## Konwencje

- Gałąź robocza: `claude/github-connection-3q9bdz`. Do `main` tylko przez PR.
- Zmiany testujemy uruchomieniem apki i zrzutem ekranu **przed** commitem.
- Komentarze i UI po polsku — zachować istniejący styl.
