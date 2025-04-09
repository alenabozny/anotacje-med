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
from utils import list_user_packs, get_user_progress_from_s3, load_json_from_s3, survey_done, update_ans_dict 

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
    <script>
        document.querySelectorAll('button').forEach(function(button) {
            if (button.textContent.trim() === 'Previous') {
                button.style.display = 'none';
            }
        });
    </script>
    """,
    unsafe_allow_html=True,
)

try:
    if st.session_state["authentication_status"]:
        # user_packs = sorted([x for x in os.listdir("data/sourcepacks_med/jsons_all") if x.endswith(f"person_{st.session_state['username'].split('_')[-1]}.json")])
        username=st.session_state['username']
        user_packs = [pack.split('_')[-3] for pack in list_user_packs(username)]
        user_progress = get_user_progress_from_s3(username)

        # Check in the annotator's folder which packs have been completed
        # Pick the pack with the highest pack number which has not been found in the list
        unfinished_packs = [x for x in user_packs if x not in user_progress]
        selected_pack = unfinished_packs[0]

        # Load survey-specific CSS
        with open("style.css", "r") as fin:
            st.markdown(f"<style>{fin.read()}</style>", unsafe_allow_html=True)

        _packpath = f"data/sourcepacks_med/jsons_all/pack_{selected_pack}_person_{username.split('_')[-1]}.json"
        contents = load_json_from_s3(_packpath)
        contents = list(contents["paraphrase"].items())

        survey = ss.StreamlitSurvey(f"pack_{selected_pack}_person_{username.split('_')[-1]}.json")
        s_pages = survey.pages(len(contents) + 1, progress_bar=True, on_submit=lambda: survey_done("Paczka ukończona. Wyniki zapisane. Dziękujemy!",
                                                                                                   selected_pack,
                                                                                                   ct_id,
                                                                                                   username=st.session_state['username']))
        with s_pages:
            st.title("Anotacje")
            st.write(f"Jesteś zalogowany jako *{st.session_state['name']}* \t|\t Anotujesz treść {s_pages.current} na {len(contents)} w paczce nr {selected_pack}")
            if s_pages.current == 0:
                st.markdown('''
                            Zaraz zaczniesz rundę anotacji fragmentów treści pochodzących z popularnonaukowych portali medycznych 
                            (medonet, hellozdrowie, itp.). Oceń ich wiarygodność na podstawie EMB, własnej intuicji oraz doświadczenia klinicznego.

- Oceniane będą „treści medyczne” z dziedziny medycyny, które są merytoryczne, obiektywnie weryfikowalne i zawierają odniesienia do EBM.
- „Treść medyczna” składa się z kilku zdań. Jeśli zdania są ze sobą logicznie powiązane, cały fragment jest oceniany łącznie. Jeśli zdania nie są logicznie powiązane, są oceniane osobno. Następnie, jeśli przynajmniej jedno z nich jest niewiarygodne, należy ocenić treść jako niewiarygodną.
- Zaleca się sprawdzenie informacji w wiarygodnych, aktualnych źródłach, jeśli treść pochodzi z dziedziny, która nie jest obszarem specjalizacji danego eksperta.

                            ''')
            else:
                current_content = contents[s_pages.current-1]
                ct_id = current_content[0]
                ct_body = current_content[1]

                sjson = survey.to_json()
                survey_dict = json.loads(sjson)
                ans_tpl = ()
                ct_id_to_save = 'empty'

                try:
                    cred_val = survey_dict['Oceń czy fragment tekstu jest Wiarygodny, Niewiarygodny czy Neutralny']["value"]
                    ct_id_to_save = survey_dict['Oceń czy fragment tekstu jest Wiarygodny, Niewiarygodny czy Neutralny']["widget_key"].split('_')[0]
                    ans_tpl = ans_tpl + (cred_val,)
                except Exception as e:
                    pass

                try:
                    unable_val = survey_dict['Dane we fragmencie są niemozliwe do weryfikacji.']["value"]
                    ans_tpl = ans_tpl + (unable_val,)
                except Exception as e:
                    pass

                try:
                    tags_val = survey_dict["Dlaczego tekst jest według Ciebie niewiarygodny:"]["value"]
                    ans_tpl = ans_tpl + (tags_val,)
                except Exception as e:
                    pass

                # log_survey_state_and_activity(survey, s_pages, selected_pack, ct_id, username)

                st.markdown(f"### {ct_id}")
                st.markdown(f"> {ct_body}")
                
                unable_to_answer = survey.checkbox("Dane we fragmencie są niemozliwe do weryfikacji.", key=f"{ct_id}_niemozliwe")

                if unable_to_answer == False:
                    cred = survey.radio(
                        "Oceń czy fragment tekstu jest Wiarygodny, Niewiarygodny czy Neutralny",
                        options=["Wiarygodny", "Neutralny", "Niewiarygodny"],
                        captions=[
                            "Wszystko się zgadza",
                            "Fragment nie dotyczy medycyny",
                            "Fałszywe informacje, wyolbrzymienie, zła interpretacja prawdziwych danych, etc.",
                        ],
                        key=f"{ct_id}_wiarygdnosc",
                        index=None
                    )
                    if cred == "Niewiarygodny":
                        survey.multiselect("Dlaczego tekst jest według Ciebie niewiarygodny:", 
                                        options=['Zawiera fałszywe informacje',
                                                    'Zawiera przedawnione/nieaktualne informacje',
                                                    'Zawiera częściowo fałszywe informacje',
                                                    'Zawiera fałszywe informacje, które są rozmyte poprzez złagodzony ton wypowiedzi',
                                                    'Zawiera informacje niemozliwe do zweryfikowania',
                                                    'Zawiera prawdziwe informacje, jednak nieproporcjonalnie wyolbrzymione',
                                                    'Zawiera prawdziwe informacje, ale sens zdania jest wypaczony przez jedno słowo'], 
                                        key=f"{ct_id}_czemu_niewiarygodne",
                                        default=None)
                    elif cred is None: # Check if the user has made a selection
                        st.error("Proszę dokonać wyboru przed kontynuacją.")
                
                update_ans_dict(ct_id_to_save, ans_tpl)
        
    else:
        switch_page("main")
except Exception as e:
    # print(e)
    switch_page("main")