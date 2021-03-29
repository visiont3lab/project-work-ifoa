import streamlit as st
import app_home, app_fede, app_leo, app_sere, app_tiz, app_update, app_province

def main():
    #st.beta_set_page_config( layout='wide')

    pages = {
        "Home": app_home,
        "App1": app_fede,
        "App2": app_leo,
        "App2" : app_sere,
        "Province": app_province,
        "Aggiornamento Dati" : app_update,
        "Zone colore dell'Italia": app_tiz
    }
    st.sidebar.title('Menu')
    selection = st.sidebar.radio("Vai a", list(pages.keys()))
    page = pages[selection]
    page.page()
    

if __name__ == '__main__':
    main()