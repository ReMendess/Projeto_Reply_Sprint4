import streamlit as st
import plotly.express as px


st.set_page_config(page_title="Análise e Dashboards")
st.title("Análise de Dados - Dashboard")


if 'sim_data' not in st.session_state:
st.info("Nenhum dado simulado encontrado. Gere simulação na página 2.")
else:
df = st.session_state['sim_data']
st.subheader("Resumo estatístico")
st.write(df.describe())


fig = px.line(df, x='time', y=['vibration','temperature'], labels={'value':'Medida','time':'Tempo'})
st.plotly_chart(fig, use_container_width=True)


st.subheader("Histograma de vibração")
fig2 = px.histogram(df, x='vibration', nbins=30)
st.plotly_chart(fig2, use_container_width=True)
