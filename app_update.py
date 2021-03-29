import streamlit as st
import utils2
import time

def page():

    st.title("Aggiorna datasets")

    col1, col2, col3 = st.beta_columns(3)
    last_update1 = utils2.last_update_choropleth()
    last_update2 = utils2.last_update_classificazione()

    with col1:
        update_button1 = st.button("Aggiorna zone per choropleth")
        st.write(f"ultimo aggiornamento: {last_update1}")

    with col2:
        update_button2 = st.button("Aggiorna zone per classificazione")
        st.write(f"ultimo aggiornamento: {last_update2}")

    #update button zone choropleth
    if update_button1:
        start = time.time()
        df_extended = utils2.update_zone_esteso()
        df_extended.to_csv("data/zone_regioni_esteso.csv")
        end = time.time()
        with col1:
            st.write("Zone aggiornate")
            st.write(f"{end - start:.2f}s")
        st.table(df_extended.tail(20))        


    #update button zone clasificazione
    if update_button2:
        start = time.time()
        df_regioni = utils2.merge_covid_w_zone()
        df_regioni.to_csv("data/ita_regioni_zone_correct.csv")
        end = time.time()
        with col2:
            st.write("Zone aggiornate")
            st.write(f"{end - start:.2f}s")
        st.table(df_regioni.tail(20))
