import streamlit as st
import app_home, app_fede, app_leo, app_sere, app_tiz, app_update, app_province

def main():
    #st.beta_set_page_config( layout='wide')

    pages = {
        "Home": app_home,
        "App1": app_leo,
        "Province": app_province,
        "Aggiornamento dati" : app_update,
        "Calcolo dell'indice Rt" : app_sere,
        "Modello predittivo per l'indice Rt" : app_fede,
        "Zone colore dell'Italia": app_tiz
    }
    st.sidebar.title('Menu')
    selection = st.sidebar.radio("Vai a", list(pages.keys()))
    page = pages[selection]
    page.page()
    

if __name__ == '__main__':
    main()