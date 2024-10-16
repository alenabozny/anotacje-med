import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import os
from streamlit_extras.switch_page_button import switch_page

# Hide the sidebar

st.set_page_config(page_title="Anotacje", initial_sidebar_state="collapsed")

st.markdown(
    """
<style>
    [data-testid="collapsedControl"] {
        display: none
    }

    div.stDeployButton {
        display: none !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

with open('creds.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

st.title("Anotacje")

name, authentication_status, username = authenticator.login('Zaloguj się', 'main')

if st.session_state["authentication_status"]:
    authenticator.logout(':no_entry_sign: Wyloguj się', 'main', key='unique_key')
    st.write(f"Jesteś zalogowany jako *{st.session_state['name']}*")

    # Serve the list of available surveys

    next_pack = st.button(":arrow_forward: Anotuj dalej")
    if next_pack:
        switch_page("survey")

    st.header('Dostępne paczki')

    user_packs = sorted([x for x in os.listdir("data/sourcepacks_med/jsons_all") if x.endswith(f"person_{st.session_state['username'].split('_')[-1]}.json")])
    with open(f"data/replies/{st.session_state['username']}/packs_done.txt", "r") as fin:
        user_progress = [x.strip() for x in fin.readlines()]

    _pack_done = ":white_check_mark: Paczka skończona"
    _pack_undone = ":white_square_button: Czeka na wykonanie"

    pack_rows = []

    for pack in user_packs:
        pack_rows.append(f"| Paczka #{pack.split('_')[1]} | {_pack_done if pack in user_progress else _pack_undone} |")

    st.markdown("| Numer paczki | Wykonana czy nie |\n| --- | --- |\n" + "\n".join(pack_rows))

    
elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')