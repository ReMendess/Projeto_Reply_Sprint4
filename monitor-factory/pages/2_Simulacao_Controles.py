import streamlit as st
import joblib
import pandas as pd
from sklearn.preprocessing import OrdinalEncoder
import matplotlib.pyplot as plt
import plotly.graph_objects as go

st.title("⚙️ Simulação de Controles")

# Carregar modelo treinado
modelo = joblib.load("./monitor-factory/model/modelo_gb.pkl")

# Escolha da máquina (só para exibição)
maq = st.sidebar.selectbox("Escolha a máquina", ["M1", "M2", "M3"])

# Upload do CSV
uploaded = st.file_uploader("📂 Anexe o CSV de sensores", type="csv")

if uploaded is not None:
    dados = pd.read_csv(uploaded)

    st.subheader(" Dados originais (anexados)")
    st.dataframe(dados.head(10))

    st.write(" Aplicando Tratamento...")

    # Mapear Tipo para L, M, H
    mapa_tipo = {"Baixa": "L", "Média": "M", "Alta": "H"}
    dados["Tipo"] = dados["Tipo"].map(mapa_tipo)

    # Criar Tipo_Encoded
    encoder = OrdinalEncoder(categories=[['L', 'M', 'H']])
    dados["Tipo_Encoded"] = encoder.fit_transform(dados[["Tipo"]])
    dados = dados.drop(["Tipo"], axis=1)

    # Features na ordem certa
    features = [
        "Temperatura do ar [K]",
        "Temperatura do processo [K]",
        "Velocidade de rotação [rpm]",
        "Torque [Nm]",
        "Desgaste ferramenta [min]",
        "Tipo_Encoded"
    ]
    X = dados[features]
    Y = dados["Falhou"]

    # Predição
    y_pred = modelo.predict(X)
    y_proba = modelo.predict_proba(X)[:, 1]

    # Resultado com predições
    dados_resultado = dados.copy()
    dados_resultado["Predição"] = y_pred
    dados_resultado["Probabilidade Falha"] = y_proba.round(3)

    st.subheader(" Resultado com Modelo")
    st.dataframe(dados_resultado.head(20))

    # --- Gráficos ---

    # Contagem das predições
    contagem = pd.Series(y_pred).value_counts().rename({0: "Normal", 1: "Falha"})
    st.subheader(" Distribuição das Predições")
    st.bar_chart(contagem)

    # Histograma das probabilidades
    st.subheader(" Distribuição das Probabilidades de Falha")
    fig, ax = plt.subplots()
    ax.hist(y_proba, bins=20, color="orange", edgecolor="black")
    ax.set_xlabel("Probabilidade de Falha")
    ax.set_ylabel("Número de Amostras")
    st.pyplot(fig)

    # Gauge com risco médio
    risco_medio = y_proba.mean()
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risco_medio,
        title={"text": "Risco Médio de Falha"},
        gauge={
            "axis": {"range": [0, 1]},
            "bar": {"color": "red"},
            "steps": [
                {"range": [0, 0.3], "color": "lightgreen"},
                {"range": [0.3, 0.7], "color": "yellow"},
                {"range": [0.7, 1], "color": "red"}
            ]
        }
    ))
    st.subheader(" Indicador de Risco Médio")
    st.plotly_chart(fig_gauge)

else:
    st.info("👉 Anexe um arquivo CSV de sensores para rodar a simulação.")
