import streamlit as st
import app_utils_it as utils



def page():
    st.title("La situazione italiana")
    st.markdown('''
        Dati dell'emergenza Covid in Italia: è possibile visualizzare alcuni grafici per le diverse statistiche 
        raccolte dalla Protezione Civile italiana.<br><br>
    ''', unsafe_allow_html=True)
    date = utils.get_date()
    col1, col2, col3= st.beta_columns(3)
    with col1:
        data_inizio = st.selectbox("Data Inzio", date[1:])
    with col2:
        data_fine = st.selectbox("Data Fine", date)
    with col3:
        nomi_regioni = utils.get_nomi_regioni() 
        nomi_regioni.insert(0,"Italia") 
        regione = st.selectbox("Analisi", nomi_regioni)
    st.table(utils.get_stats(regione,data_inizio,data_fine))
    options = st.multiselect("Seleziona", utils.get_options(),default=utils.get_options())
    fig_stats = utils.fig_stats(regione,data_inizio,data_fine,options)
    fig_stats_variation = utils.fig_stats_variation(regione,data_inizio,data_fine,options)

    st.plotly_chart(fig_stats, use_container_width=True)
    st.plotly_chart(fig_stats_variation, use_container_width=True)