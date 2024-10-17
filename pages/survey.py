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
        /* Hide the Previous button */
        [data-testid="baseButton-secondary"] {
            display: none;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

try:
    if st.session_state["authentication_status"]:
        user_packs = sorted([x for x in os.listdir("data/sourcepacks_med/jsons_all") if x.endswith(f"person_{st.session_state['username'].split('_')[-1]}.json")])

        with open(f"data/replies/{st.session_state['username']}/packs_done.txt", "r") as fin:
            user_progress = [x.strip() for x in fin.readlines()]

        # Check in the annotator's folder which packs have been completed
        # Pick the pack with the highest pack number which has not been found in the list
        unfinished_packs = [x for x in user_packs if x not in user_progress]
        selected_pack = unfinished_packs[0]


        # Load survey-specific CSS
        with open("style.css", "r") as fin:
            st.markdown(f"<style>{fin.read()}</style>", unsafe_allow_html=True)

        _packpath = f"data/sourcepacks_med/jsons_all/{selected_pack}"

        with open(_packpath, "r") as inf:
            contents = json.load(inf)

        contents = list(contents["paraphrase"].items())

        survey = ss.StreamlitSurvey(f"{_packpath.split('/')[-1]}")

        # on-submit function for the survey
        def survey_done(success_string):
            st.success(success_string)
            with open(f"data/replies/{st.session_state['username']}/finished/finished_{selected_pack}", 'w') as outf:
                outf.write(survey.to_json())
            
            with open(f"data/replies/{st.session_state['username']}/packs_done.txt", "a") as fout:
                fout.write(f"{selected_pack}\n")
            
            with open(f"data/replies/{st.session_state['username']}/logs/general.txt", "a") as fout:
                fout.write(f"FINISHED Pack\t{selected_pack}\tTimestamp\t{time.time()}\tCtID\t{ct_id}\n")
            
            switch_page("main")

        import inspect
        s_pages = survey.pages(len(contents) + 1, progress_bar=True, on_submit=lambda: survey_done("Paczka ukończona. Wyniki zapisane. Dziękujemy!"))

        with s_pages:
            st.title("Anotacje")
            st.write(f"Jesteś zalogowany jako *{st.session_state['name']}* \t|\t Anotujesz tweet {s_pages.current} na {len(contents)} w paczce nr {selected_pack.split('_')[1]}")
            if s_pages.current == 0:
                st.markdown(f"Tutaj jest miejsce na opis rundy do anotacji.")
            else:
                current_content = contents[s_pages.current - 1]
                ct_id = current_content[0]
                ct_body = current_content[1]

                if s_pages.current > 0:
                    # Logging current state of the survey after each question
                    with open(f"data/replies/{st.session_state['username']}/logs/{selected_pack.removesuffix('.json')}_last_state.json", "a") as fout:
                        fout.write(f"--- time {time.time()} | page {s_pages.current} ---\n")
                        fout.write(survey.to_json())
                    
                    # Also, log activity, i.e. page, time and content id
                    with open(f"data/replies/{st.session_state['username']}/logs/general.txt", "a") as fout:
                        fout.write(f"Pack\t{selected_pack}\tPage\t{s_pages.current}\tTimestamp\t{time.time()}\tContentID\t{ct_id}\n")

                st.markdown(f"> {ct_body}")
                
                cred = survey.radio(
                    "Oceń czy fragment tekstu jest Wiarygodny, Niewiarygodny czy Neutralny",
                    options=["Wiarygodny", "Neutralny", "Niewiarygodny"],
                    # captions=[
                    #     "Wszystko się zgadza",
                    #     "Fragment nie dotyczy medycyny",
                    #     "Fałszywe informacje, wyolbrzymienie, zła interpretacja danych, etc.",
                    # ],
                    key=f"{ct_id}_wiarygdnosc"
                )
                if cred == "Niewiarygodny":
                    survey.multiselect("Dlaczego tekst jest według Ciebie niewiarygodny:", options=["a","b","c"], key=f"{ct_id}_czemu_niewiarygodne")
                
                survey.checkbox("Dane we fragmencie są niemozliwe do weryfikacji.", key=f"{ct_id}_niemozliwe")
        
    else:
        switch_page("main")
except Exception as e:
    print(e)
    switch_page("main")