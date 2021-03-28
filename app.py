import streamlit as st
import app_home, app_fede, app_leo, app_sere, app_tiz

def main():

    pages = {
        "Home": app_home,
        "App1": app_fede,
        "App2": app_leo,
        "App3": app_sere,
        "Zone colore dell'Italia": app_tiz
    }
    st.sidebar.title('Menu')
    selection = st.sidebar.radio("Vai a", list(pages.keys()))
    page = pages[selection]
    page.page()
    

if __name__ == '__main__':
    main()