import streamlit as st
# import pandas as pd
# import numpy as np
import streamlit_survey as ss
import json
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from uuid import uuid4
import os
from streamlit_extras.switch_page_button import switch_page
import time

# Hide the sidebar

st.set_page_config(initial_sidebar_state="collapsed")

st.markdown(
    """
<style>
    [data-testid="collapsedControl"] {
        display: none
    }
</style>
""",
    unsafe_allow_html=True,
)

try:
    if st.session_state["authentication_status"]:
        user_packs = sorted([x for x in os.listdir("data/sourcepacks/jsons_all") if x.endswith(f"person_{st.session_state['username'].split('_')[-1]}.json")])
        user_packs = [user_packs[-1]] + user_packs [:-1]
        with open(f"data/replies/{st.session_state['username']}/packs_done.txt", "r") as fin:
            user_progress = [x.strip() for x in fin.readlines()]

        # Check in the annotator's folder which packs have been completed
        # Pick the pack with the highest pack number which has not been found in the list
        unfinished_packs = [x for x in user_packs if x not in user_progress]
        selected_pack = unfinished_packs[0]

        # Load survey-specific CSS
        with open("style.css", "r") as fin:
            st.markdown(f"<style>{fin.read()}</style>", unsafe_allow_html=True)

        # # Serve a survey for the selected pack
        # # Check if survey is in progress - if part of it was already done;
        # # if yes, load it from the stop point
        # # else, get a new one

        # if os.path.isfile(f"data/replies/{st.session_state['username']}/logs/{selected_pack.removesuffix('.json')}_last_state.json"):
        #     with open(f"data/replies/{st.session_state['username']}/logs/{selected_pack.removesuffix('.json')}_last_state.json", "r") as log:
        #         _last_page_logged = log.readline().strip()
        #         print(_last_page_logged)



        _packpath = f"data/sourcepacks/jsons_all/{selected_pack}"

        with open(_packpath, "r") as inf:
            tweets = json.load(inf)

        tweets = list(tweets["orig_tweet_text"].items())

        survey = ss.StreamlitSurvey(f"{_packpath.split('/')[-1]}")

        # on-submit function for the survey
        def survey_done(success_string):
            st.success(success_string)
            with open(f"data/replies/{st.session_state['username']}/finished/finished_{selected_pack}", 'w') as outf:
                outf.write(survey.to_json())
            
            with open(f"data/replies/{st.session_state['username']}/packs_done.txt", "a") as fout:
                fout.write(f"{selected_pack}\n")
            
            with open(f"data/replies/{st.session_state['username']}/logs/general.txt", "a") as fout:
                fout.write(f"FINISHED Pack\t{selected_pack}\tTimestamp\t{time.time()}\tTweetID\t{tw_id}\n")
            
            switch_page("main")


        s_pages = survey.pages(len(tweets) + 1, on_submit=lambda: survey_done("Paczka ukończona. Wyniki zapisane. Dziękujemy!"))


        with s_pages:
            st.title("Anotacje")
            st.write(f"Jesteś zalogowany jako *{st.session_state['name']}* \t|\t Anotujesz tweet {s_pages.current} na {len(tweets)} w paczce nr {selected_pack.split('_')[3]}")
            if s_pages.current == 0:
                st.markdown(f"> Drogi anotatorze, witaj w badaniu dotyczącym analizy dyskursu w polskich social mediach. W tej paczce ocenisz {len(tweets)} tweetów pod kątem zabarwienia emocjonalnego, występowania ironii oraz bycia na temat wojny w Ukrainie lub pandemii COVID-19.")
                
                st.markdown(f"> Nie ma limitu czasu na odpowiedź, ale nie zastanawiaj się zbyt długo nad jednym tweetem. Zależy nam bardziej na szczerych reakcjach niż na dogłębnych analizach. Czas odpowiedzi będzie jednym z parametrów modelu, więc nie zwlekaj niepotrzebnie i nie zostawiaj ankiety włączonej, gdy odchodzisz od komputera. Dostępny jest przycisk poprzedniej strony, gdybyś koniecznie musiał/a coś poprawić. Spróbuj zawsze dokończyć rozpoczętą paczkę w jednej sesji. __Jeśli porzucisz ankietę w trakcie paczki, postęp nie zapisze się.__")

                st.markdown(f"> Liczba pytań pod tweetem będzie się wahać od czterech do sześciu, w zależności od twoich wcześniejszych odpowiedzi.")

                st.markdown(f"> Treść tweeta wyświetla się dwa razy, nad i pod pytaniami, aby była zawsze widoczna w trakcie udzielania odpowiedzi.")

                st.markdown(f"> Jeśli tweet jest zbyt krótki, niejasny lub pozbawiony kontekstu i w związku z tym nie jesteś w stanie go ocenić, zaznacz pole na dole strony.")

                st.markdown(f"> Na górze strony możesz śledzić swój postęp w danej paczce. Na stronie głównej portalu zobaczysz swój postęp całkowity.")

                st.markdown(f"> Portal przystosowany jest do odczytu w trybie jasnym systemu i przeglądarki. Gdyby tryb ciemny uniemożliwiał lub pogarszał czytelność, zmień go na jasny w ustawieniach w prawym górnym rogu, tj.: kliknij trzy kropki => Settings => Theme: Light.")

                st.markdown(f"> Przez pierwszych kilka dni mogą wystąpić przerwy w pracy platformy ze względu na zmiany w konfiguracji serwera. Dział IT już nad tym pracuje. W razie problemów technicznych, pisz na bjastrzebski@kozminski.edu.pl.")

                st.markdown(f" > Dziękujemy za pomoc i powodzenia!")
            else:
                current_tweet = tweets[s_pages.current - 1]
                tw_id = current_tweet[0]
                tw_text = current_tweet[1]

                if s_pages.current > 1:
                    # Logging current state of the survey after each question
                    with open(f"data/replies/{st.session_state['username']}/logs/{selected_pack.removesuffix('.json')}_last_state.json", "w") as fout:
                        fout.write(f"--- time {time.time()} | page {s_pages.current} ---\n")
                        fout.write(survey.to_json())
                    
                    # Also, log activity, i.e. page, time and tweet id
                    with open(f"data/replies/{st.session_state['username']}/logs/general.txt", "a") as fout:
                        fout.write(f"Pack\t{selected_pack}\tPage\t{s_pages.current}\tTimestamp\t{time.time()}\tTweetID\t{tw_id}\n")

                st.markdown(f"> {tw_text}")
                akt_zabarwienie = survey.select_slider("Oceń zabarwienie emocjonalne tweeta od 1 (Bardzo negatywne) do 7 (Bardzo pozytywne):", options=["Bardzo negatywne", "2", "3", "Neutralne", "5", "6", "Bardzo pozytywne"], value="Neutralne", id=f"TW_{tw_id}_zabarwienie_emocjonalne")

                akt_ironia = survey.select_slider("Oceń w jakim stopniu ten tweet jest ironiczny od 1 (Nieironiczny) do 7 (Bardzo ironiczny)", options=["Nieironiczny", "2", "3", "4", "5", "6", "Bardzo ironiczny"], value="Nieironiczny", id=f"TW_{tw_id}_ironia")

                akt_ua = survey.select_slider("Oceń w jakim stopniu ten tweet dotyczy wojny w Ukrainie lub Ukraińców od 1 (W ogóle nie dotyczy) do 7 (Dotyczy wyłącznie)", options=["W ogóle nie dotyczy", "2", "3", "4", "5", "6", "Dotyczy wyłącznie"], value="W ogóle nie dotyczy", id=f"TW_{tw_id}_temat_UA")

                if akt_ua != "W ogóle nie dotyczy":
                    survey.select_slider("Oceń nastawienie autora tweeta do Ukrainy lub Ukraińców od 1 (Bardzo negatywne) do 7 (Bardzo pozytywne):", options=["Bardzo negatywne", "2", "3", "Neutralne", "5", "6", "Bardzo pozytywne"], value="Neutralne", id=f"TW_{tw_id}_nastawienie_UA")
                
                akt_covid = survey.select_slider("Oceń w jakim stopniu ten tweet dotyczy COVID-19 od 1 (W ogóle nie dotyczy) do 7 (Dotyczy wyłącznie)", options=["W ogóle nie dotyczy", "2", "3", "4", "5", "6", "Dotyczy wyłącznie"], value="W ogóle nie dotyczy", id=f"TW_{tw_id}_temat_COVID")

                if akt_covid != "W ogóle nie dotyczy":
                    survey.select_slider("Oceń nastawienie autora tweeta do środków prewencji przeciw COVID-19 (szczepienia, maseczki, lockdowny, certyfikaty, etc.) od 1 (Bardzo negatywne) do 7 (Bardzo pozytywne):", options=["Bardzo negatywne", "2", "3", "Neutralne", "5", "6", "Bardzo pozytywne"], value="Neutralne", id=f"TW_{tw_id}_nastawienie_COVID")
                
                st.markdown(f"> {tw_text}")

                survey.checkbox("Ten tweet jest zbyt krótki lub niejasny i nie potrafię go zinterpretować.", id=f"TW_{tw_id}_bad_tweet")

                # st.markdown(f"> {tw_text}")
        
    else:
        switch_page("main")
except:
    switch_page("main")