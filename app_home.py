import streamlit as st
import streamlit.components.v1 as components


def page():
    st.title('Analisi dei dati "Covid-19"')
    st.subheader('Studio della situazione in Italia - il progetto')
    st.markdown('''
        Questa web app è stata creata come progetto di gruppo del corso di Machine Learning di IFOA nel contesto del DataLab (https://www.bigdata-lab.it/).
        
        Le analisi si basano sui dati pubblici rilasciati dalla Protezione Civile italiana durante l'emergenza Covid del 2020-2021.

        Qui di seguito si può avere una visione d'insieme delle statistiche dei dati sino ad oggi raccolti.<br><br>
    ''', unsafe_allow_html=True)

    
    # st.markdown('''
    # <br><br>
    # <iframe src='https://flo.uri.sh/story/722265/embed' title='Interactive or visual content' frameborder='0' scrolling='no' style='width:100%;height:900px;' sandbox='allow-same-origin allow-forms allow-scripts allow-downloads allow-popups allow-popups-to-escape-sandbox allow-top-navigation-by-user-activation'></iframe>
    # <div style='width:100%!;margin-top:4px!important;text-align:right!important;'>
    #     <a class='flourish-credit' href='https://public.flourish.studio/story/722265/?utm_source=embed&utm_campaign=story/722265' target='_top' style='text-decoration:none!important'>
    #         <img alt='Made with Flourish' src='https://public.flourish.studio/resources/made_with_flourish.svg' style='width:105px!important;height:16px!important;border:none!important;margin:0!important;'>
    #     </a>
    # </div>
    # ''', unsafe_allow_html=True)
    st.subheader("Bar Chart Race totale positivi")
    components.iframe('https://flo.uri.sh/visualisation/5715327/embed', 800, 600)

