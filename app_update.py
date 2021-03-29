import streamlit as st
import utils2
import time

def page():

    st.title("Aggiorna datasets")
    
    if st.button("Aggiorna zone per choropleth"):
        start = time.time()
        df_extended = utils2.update_zone_esteso()
        df_extended.to_csv("data/zone_regioni_esteso.csv")
        end = time.time()
        st.write("Zone aggiornate")
        st.write(f"{end - start}s")
        st.table(df_extended.tail(20))


    if st.button("Aggiorna zone per classificazione"):
        start = time.time()
        df_regioni = utils2.merge_covid_w_zone()
        df_regioni.to_csv("data/ita_regioni_zone_correct.csv")
        end = time.time()
        st.write("Zone aggiornate")
        st.write(f"{end - start}s")
        st.table(df_regioni.tail(20))