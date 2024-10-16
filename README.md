# anotacje-med
Platforma do anotacji wiarygodności danych medycznych
# anotacje-platforma
 Prosta platforma do zbierania anotacji bez ingerencji w dane

 ## Zamiast dokumentacji
 1. generate_credentials.py generuje wybraną liczbę uzytkowników wraz z hasłami oraz produkuje output (w pliku) do wklejenia w część "credentials" pliku konfiguracyjnego creds.yaml, z którego korzysta aplikacja w streamlicie.
 2. Dla kazdego z tych uzytkownikow nalezy stworzyc folder i puste pliki w data/replies według wzoru podanego w data/replies/anotator_test
 3. Aplikacja przeszukuje data/sourcepacks/jsons_all i udostępnia uzytkownikowi do anotacji wszystkie paczki kończące się na person_{numer_uzytkownika_po_prefiksie}. Odpowiedzi zapisują się w data/replies/anotator_{numer_uzytkownika_po_prefiksie}. Paczki nalezy wygenerować we własnym zakresie. Mogę w późniejszym terminie udostępnić swój kod do randomizacji, dzielenia, uwzględniania wspólnych tweetów, etc., ale to juz jest bardzo task-specific, więc nie sądzę aby był specjalnie przydatny.
 4. Template'y zakodowane na stałe w plikach: main.py, pages/survey_template.py oraz pages/survey.py. Do zmiany według potrzeby.
 5. Dołączam skrypt do czyszczenia postępów na potrzeby testu (reset_user_progress.py).
 6. Dołączam skrypt do podtrzymywania serwera przy zyciu (keep_running.sh).
 7. Ta platforma to MVP na potrzeby anotacji w projekcie Medfake. Słabo się skaluje, więc zawsze sprawdź czy masz wystarczające zasoby. Testowana do maksymalnie ca. 20 jednoczesnych uzytkownikow.
