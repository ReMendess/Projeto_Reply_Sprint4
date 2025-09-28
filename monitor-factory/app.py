import streamlit as st


st.set_page_config(page_title="Monitoramento em Tempo real", layout="wide")


st.title("Painel")
st.markdown("Use o menu lateral para navegar entre as páginas.")


st.sidebar.title("Navegação")
st.sidebar.info("As páginas estão em `pages/` — Streamlit carrega automaticamente.")


st.sidebar.markdown("**Rodar local:** `streamlit run app.py`")


st.write("Abra as páginas no menu lateral (1 a 4).")
