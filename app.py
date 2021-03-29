import streamlit as st
import app_home, app_fede, app_leo, app_sere, app_tiz, app_update, app_province

def main():
    #st.beta_set_page_config( layout='wide')

    pages = {
        "Il progetto": app_home,
        "App1": app_leo,
        "Conteggio delle positività": app_province,
        "Calcolo dell'indice Rt" : app_sere,
        "Modello predittivo per l'indice Rt" : app_fede,
        "Zone colore dell'Italia": app_tiz,
        "Aggiornamento dati" : app_update
    }
    st.sidebar.title('Menu')
    selection = st.sidebar.radio("Vai a", list(pages.keys()))
    page = pages[selection]
    page.page()
    

if __name__ == '__main__':
    main()