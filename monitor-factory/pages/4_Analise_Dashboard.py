# arquivo: pagina3_dashboards.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.title("Dashboards Interativos de Leituras de Sensores")

# ==============================
# Dados
# ==============================
if "hist" not in st.session_state or not st.session_state.hist:
    st.info("Nenhum dado disponível ainda. Execute a simulação na Página 2 ou faça upload de um CSV.")
    uploaded = st.file_uploader("Ou anexe o CSV de sensores", type="csv")
    if uploaded:
        dados_raw = pd.read_csv(uploaded)
        st.session_state.hist = dados_raw.to_dict("records")
    else:
        st.stop()

# Converte histórico para DataFrame
df = pd.DataFrame(st.session_state.hist)

# ==============================
# Filtros Interativos
# ==============================
st.sidebar.header("Filtros")
num_leituras = st.sidebar.slider("Número de leituras para visualizar", min_value=10, max_value=len(df), value=30, step=5)
filtro_tipo = st.sidebar.multiselect("Tipos de processo", options=df["Tipo"].unique() if "Tipo" in df.columns else [], default=df["Tipo"].unique() if "Tipo" in df.columns else [])

df_filtrado = df.tail(num_leituras)
if filtro_tipo and "Tipo" in df.columns:
    df_filtrado = df_filtrado[df_filtrado["Tipo"].isin(filtro_tipo)]

# ==============================
# Dashboard 1: Probabilidade de Falha
# ==============================
st.subheader("Risco de Falha ao Longo do Tempo")
fig_prob = go.Figure()
fig_prob.add_trace(go.Scatter(
    x=df_filtrado.index,
    y=df_filtrado["Probabilidade Falha"],
    mode="lines+markers",
    line=dict(color="red"),
    name="Probabilidade de Falha"
))
fig_prob.update_layout(
    yaxis=dict(range=[0, 1]),
    xaxis_title="Leitura",
    yaxis_title="Probabilidade de Falha"
)
st.plotly_chart(fig_prob, use_container_width=True)

# ==============================
# Dashboard 2: Distribuição de Predições
# ==============================
st.subheader("Distribuição de Predições (Normal x Falha)")
pred_counts = df_filtrado["Predição"].value_counts().rename({0: "Normal", 1: "Falha"})
fig_pred = px.pie(values=pred_counts.values, names=pred_counts.index, color=pred_counts.index,
                  color_discrete_map={"Normal": "green", "Falha": "red"})
st.plotly_chart(fig_pred, use_container_width=True)

# ==============================
# Dashboard 3: Sensores ao Longo do Tempo
# ==============================
st.subheader("Valores dos Sensores ao Longo do Tempo")
sensores = ["Temperatura do ar [K]", "Temperatura do processo [K]", "Velocidade de rotação [rpm]", "Torque [Nm]", "Desgaste ferramenta [min]"]
sensor_selec = st.multiselect("Selecione sensores para visualizar", options=sensores, default=sensores[:3])

if sensor_selec:
    fig_sensores = go.Figure()
    for sensor in sensor_selec:
        if sensor in df_filtrado.columns:
            fig_sensores.add_trace(go.Scatter(
                x=df_filtrado.index,
                y=df_filtrado[sensor],
                mode="lines+markers",
                name=sensor
            ))
    st.plotly_chart(fig_sensores, use_container_width=True)

# ==============================
# Dashboard 4: Heatmap de Correlação
# ==============================
st.subheader("Heatmap de Correlação entre Sensores")
corr_cols = [col for col in sensores if col in df_filtrado.columns]
if corr_cols:
    corr = df_filtrado[corr_cols].corr()
    fig_corr = px.imshow(corr, text_auto=True, aspect="auto", color_continuous_scale="RdBu_r", origin="lower")
    st.plotly_chart(fig_corr, use_container_width=True)
