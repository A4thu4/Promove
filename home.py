import streamlit as st

st.set_page_config(page_title="Simuladores PROMOVE", page_icon="assets/Brasão.png", layout="wide")

# CSS para remover o botão de abrir o menu lateral (opcional)
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {display: none;}
    </style>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("assets/Logomarca_GNCP_transparente.png", width=800)   


st.title("Portal de Simuladores PROMOVE")

from streamlit_option_menu import option_menu

selected = option_menu(
    menu_title=None, 
    options=["Início", "GERAL", "UEG"], 
    icons=["house", "graph-up", "mortarboard"], 
    orientation="vert",
)

if selected == "GERAL":
    st.switch_page("pages/GERAL.py")
elif selected == "UEG":
    st.switch_page("pages/UEG.py")    