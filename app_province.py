import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, time, timedelta, date
import numpy as np
import app_utils

def page():
    st.title("Sunburst plot")
    st.markdown('## Covid 19: dataset province')
    col1, col2 = st.beta_columns(2)
    with col1:
        fig1 = app_utils.fig_sunburst('totale_casi', "Totale casi")
        st.plotly_chart(fig1, use_container_width=True)
            
    with col2:
        fig2 = app_utils.fig_sunburst('densità_casi','Densità di casi per popolazione' )
        st.plotly_chart(fig2, use_container_width=True)

    st.plotly_chart(fig1, use_container_width=True)
    st.plotly_chart(fig2, use_container_width=True)