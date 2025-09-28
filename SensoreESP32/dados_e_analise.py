import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import time

# Função de criar dados simulads
def dados_wokwi(n_samples=3000):
    np.random.seed(555)
    time.sleep(1.5)
    st.info("Carregando data set. . .")

    dados_temperatura = np.random.normal(loc=27, scale=2, size=n_samples)
    dados_umidade =  np.random.beta(a=2, b=5, size=n_samples) * 100
    acc_x = np.random.normal(loc=0, scale=0.3, size=n_samples)
    acc_y = np.random.normal(loc=0, scale=0.3, size=n_samples)
    acc_z = np.random.normal(loc=9.81, scale=0.4, size=n_samples)
    vibracao_total = np.sqrt(acc_x ** 2 + acc_y ** 2 + (acc_z - 9.81) ** 2)
    corrente = np.random.lognormal(mean=np.log(5), sigma=0.3, size=n_samples)

    df = pd.DataFrame({
        'Temperatura': dados_temperatura,
        'Umidade': dados_umidade,
        'Vibração': vibracao_total,
        'Corrente': corrente
    })
    return df

# Aplicação
st.title("Reply - Fase 2")
st.title("Análise Exploratória de Dados Simulados - Wokwi")

# Sidebar para entrada do número de amostras
n_samples = st.sidebar.slider("Número de amostras", min_value=500, max_value=5000, value=3000, step=500)

# Inicializa session_state se ainda não tiver dados
if 'df' not in st.session_state:
    st.session_state.df = None

# Botão para carregar os dados
if st.sidebar.button("Gerar dados"):
    st.session_state.df = dados_wokwi(n_samples)
    st.success("Dados carregados com sucesso!")

# Se os dados já estiverem carregados
if st.session_state.df is not None:
    df = st.session_state.df

    st.subheader("Prévia dos Dados")
    st.dataframe(df.head())

    st.subheader("Estatísticas Descritivas")
    st.write(df.describe())

    # Gráficos interativos
    st.subheader("Gráfico de Dispersão")
    x_axis = st.selectbox("Eixo X", df.columns, index=0)
    y_axis = st.selectbox("Eixo Y", df.columns, index=1)
    fig1 = px.scatter(df, x=x_axis, y=y_axis, color=y_axis, title=f"{y_axis} vs {x_axis}")
    st.plotly_chart(fig1)

    st.subheader("Histograma")
    hist_col = st.selectbox("Selecionar variável para histograma", df.columns, index=2)
    fig2 = px.histogram(df, x=hist_col, nbins=40, title=f"Distribuição de {hist_col}")
    st.plotly_chart(fig2)

    st.subheader("Boxplot")
    box_col = st.selectbox("Selecionar variável para boxplot", df.columns, index=3)
    fig3 = px.box(df, y=box_col, title=f"Boxplot de {box_col}")
    st.plotly_chart(fig3)
else:
    st.warning("Clique em 'Gerar dados' para iniciar a análise.")


