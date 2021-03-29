import streamlit as st
import app_home, app_fede, app_leo, app_sere, app_tiz, app_update, app_provincie
import pandas as pd
import numpy as np
import json
from zipfile import ZipFile
import wget
from datetime import datetime as dt

def main():
    st.beta_set_page_config( layout='wide')

    pages = {
        "Home": app_home,
        "App1": app_fede,
        "App2": app_leo,
        "App2" : app_sere,
        "Provincie": app_provincie,
        "Aggiorna Dati" : app_update,
        "Zone colore dell'Italia": app_tiz
    }
    st.sidebar.title('Menu')
    selection = st.sidebar.radio("Vai a", list(pages.keys()))
    page = pages[selection]
    page.page()
    

if __name__ == '__main__':
    main()