import streamlit as st
import app_utils
import time


def page():

    st.title('Aggiornamento datasets')
    st.markdown('''
    In questa pagina è possibile effettuare gli aggiornamenti per includere nell'analisi i dati più recenti disponibili.
    <br>
    <br>
    <br>
    ''', unsafe_allow_html=True)

    col1, col2, col3 = st.beta_columns(3)
    last_update1 = app_utils.last_update_choropleth()
    last_update2 = app_utils.last_update_classificazione()

    with col1:
        update_button1 = st.button("Aggiorna zone per mappe di colore")
        st.write(f"ultimo aggiornamento: {last_update1}")

    with col2:
        update_button2 = st.button("Aggiorna zone ed indice Rt per classificazione")
        st.write(f"ultimo aggiornamento: {last_update2}")

    #update button zone choropleth
    if update_button1:
        start = time.time()
        df_extended = app_utils.update_zone_esteso()
        df_extended.to_csv("data/zone_regioni_esteso.csv")
        end = time.time()
        with col1:
            st.write("Zone aggiornate")
            st.write(f"Tempo impiegato: {end - start:.2f}s")
        st.table(df_extended.tail(20))        


    #update button zone e rt classificazione
    if update_button2:
        start = time.time()
        df_r = app_utils.merge_covid_w_zone()
        df_rt = app_utils.get_rt_index()
        df_r, missing_dates = app_utils.merge_covid_w_rt(df_r, df_rt)
        df_r.to_csv("data/ita_regioni_zone_correct.csv")
        end = time.time()
        with col2:
            st.write("Zone ed indice Rt aggiornati")
            st.write(f"Tempo impiegato: {end - start:.2f}s")
            st.write(f"Seguenti date non disponibili per indice Rt: {missing_dates}")
        st.table(df_r.tail(20))
