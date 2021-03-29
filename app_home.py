import streamlit as st

def page():
    st.title('Analisi dei dati "Covid-19"')
    st.subheader('Studio della situazione in Italia - il progetto')
    st.markdown('''
        Questa web app è stata creata come progetto di gruppo del corso di Machine Learning di IFOA nel contesto del DataLab (https://www.bigdata-lab.it/).
        
        Le analisi si basano sui dati pubblici rilasciati dalla Protezione Civile italiana durante l'emergenza Covid del 2020-2021.
    ''')
