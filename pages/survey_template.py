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

with open("../style.css", "r") as fin:
    st.markdown(f"<style>{fin.read()}</style>", unsafe_allow_html=True)

_packpath = "data/sourcepacks/jsons_all/globalpack_398_pack_8_person_39.json"

with open(_packpath, "r") as inf:
    tweets = json.load(inf)

tweets = list(tweets["orig_tweet_text"].items())

survey = ss.StreamlitSurvey(f"{_packpath.split('/')[-1]}")

s_pages = survey.pages(len(tweets) + 1, on_submit=lambda: st.success("Paczka ukończona. Wyniki zapisane. Dziękujemy!"))


with s_pages:
    if s_pages.current == 0:
        st.write("Tutaj instrukcje")
    else:
        current_tweet = tweets[s_pages.current - 1]
        tw_id = current_tweet[0]
        tw_text = current_tweet[1]

        if s_pages.current > 1:
            # Logging current state of the survey after each question
            # with open()
            #     tw_id
            #     survey.to_json()
            pass

        st.write(f"{s_pages.current}/{len(tweets)}")

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