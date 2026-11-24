# Cozy Box by Kim – plan startu sklepu

Stan na koniec dnia pracy. Następna sesja zaczyna od sekcji „Do zrobienia”.

## Gotowe

- Przegląd kodu `app.py` (Streamlit): 5 zakładek, koszyk, formularz zamówienia, panel sprzedawcy.
- Lista startowa dla Kim jako strona Claude (artefakt) z zapisem odpowiedzi, wgrywaniem plików,
  linkami z Google Drive i przyciskiem „Wyślij”: https://claude.ai/artifact/P2gi3axJZBQvDrmDLkA26Q
  - Odpowiedzi trafiają do kolekcji `answers`, wysłane zgłoszenia do `submissions`.
  - Wysyłka zgłoszeń mailem działa na razie ręcznie: Claude odczytuje zgłoszenie i wysyła maila.
    Automatyczna wysyłka co godzinę wymaga osobnej zgody na zadanie cykliczne.

## Do zrobienia

1. Dokończyć test listy z konta gościa spoza organizacji: wpis w pole, plik, link z Drive, „Wyślij”.
   Potem napisać do Claude „sprawdź test”.
2. Usunąć puste zgłoszenie testowe z 24.09 z kolekcji `submissions`.
3. Udostępnić listę Kim (zaproszenie imienne z prawem edycji) i wysłać jej link.
4. Po wypełnieniu listy przez Kim wprowadzić zmiany w `app.py`:
   - zapis zamówień w Google Sheets zamiast `data/orders.csv` (dysk Streamlit Cloud jest tymczasowy),
   - hasło panelu tylko w Secrets, bez domyślnego `cozybox2025` w kodzie,
   - linki do Instagrama i TikToka, stopka z danymi sprzedawcy,
   - dane do płatności po zamówieniu (konto, BLIK, tytuł = numer zamówienia),
   - stany magazynowe i „wyprzedane”,
   - termin wysyłki, przycisk „Zamawiam z obowiązkiem zapłaty”,
   - powiadomienia e-mail o nowych zamówieniach.
5. Przygotować projekty: regulamin, polityka prywatności, formularz odstąpienia od umowy.

## Ważne

- Repozytorium jest publiczne: żadnych danych osobowych ani haseł w kodzie i w tym pliku.
