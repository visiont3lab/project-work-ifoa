import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, time, timedelta, date
import numpy as np
import app_utils

def page():
 

    st.title('Conteggio delle positività')
    st.subheader('Suddivisione regionale e provinciale.')
    st.markdown('Casi di pazienti positivi al Covid-19 aggiornati rispetto ai dati più recenti.')


    fig1 = app_utils.fig_sunburst('totale_casi', "Totale casi")
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = app_utils.fig_sunburst('densità_casi','Densità di casi per popolazione' )
    st.plotly_chart(fig2, use_container_width=True)
