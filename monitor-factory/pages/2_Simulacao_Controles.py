import streamlit as st
import joblib
import pandas as pd
from sklearn.preprocessing import OrdinalEncoder
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
st.title(" Simulação de Controles em Tempo Real (30s)")

# ===== Config =====
INTERVALO_MS = 5_000  # 30 segundos

# ===== Estado =====
if "idx" not in st.session_state:
    st.session_state.idx = 0
if "hist" not in st.session_state:
    st.session_state.hist = []  # lista de dicts

# Botão de reset
cols_top = st.columns([1, 1, 3])
with cols_top[0]:
    if st.button("🔄 Reset simulação"):
        st.session_state.idx = 0
        st.session_state.hist = []
        st.rerun()

# Carregar modelo treinado
modelo = joblib.load("modelo_gb.pkl")

# Upload do CSV
uploaded = st.file_uploader(" Anexe o CSV de sensores", type="csv")

if uploaded is None:
    st.info(" Anexe um arquivo CSV de sensores para iniciar a simulação.")
    st.stop()

# Carrega e pré-processa
dados_raw = pd.read_csv(uploaded)

# Mapeia Tipo e cria Tipo_Encoded
mapa_tipo = {"Baixa": "L", "Média": "M", "Alta": "H"}
dados = dados_raw.copy()
dados["Tipo"] = dados["Tipo"].map(mapa_tipo)

encoder = OrdinalEncoder(categories=[['L', 'M', 'H']])
dados["Tipo_Encoded"] = encoder.fit_transform(dados[["Tipo"]])
dados = dados.drop(columns=["Tipo"])

features = [
    "Temperatura do ar [K]",
    "Temperatura do processo [K]",
    "Velocidade de rotação [rpm]",
    "Torque [Nm]",
    "Desgaste ferramenta [min]",
    "Tipo_Encoded"
]

# Proteção para índice além do fim
if st.session_state.idx >= len(dados):
    st.success("✅ Fim do arquivo — todas as leituras foram processadas.")
    if st.session_state.hist:
        st.dataframe(pd.DataFrame(st.session_state.hist))
    st.stop()

# ===== Tick (a cada 30s) =====
# 🔥 Atualiza o app a cada 30s automaticamente
st_autorefresh(interval=INTERVALO_MS, key="tick_30s")

# ===== Processa a próxima linha =====
i = st.session_state.idx
linha = dados.iloc[i]
X = linha[features].values.reshape(1, -1)
y_pred = modelo.predict(X)[0]
y_proba = float(modelo.predict_proba(X)[0, 1])

status_txt = " Normal" if y_pred == 0 else " Falha detectada!"
status_cor = "green" if y_pred == 0 else "red"

# Guarda no histórico
registro = {
    "Leitura": i + 1,
    **{k: dados_raw.iloc[i][k] if k in dados_raw.columns else linha.get(k, None) for k in dados_raw.columns},
    "Predição": int(y_pred),
    "Probabilidade Falha": round(y_proba, 3)
}
st.session_state.hist.append(registro)

# ===== UI: Última leitura =====
st.subheader(f"📡 Última leitura (#{i+1}) — atualiza a cada 30s")
colA, colB = st.columns([2, 1])
with colA:
    st.json(registro)
with colB:
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=y_proba,
        title={"text": "Risco de Falha"},
        gauge={
            "axis": {"range": [0, 1]},
            "bar": {"color": "red" if y_pred else "green"},
            "steps": [
                {"range": [0, 0.3], "color": "lightgreen"},
                {"range": [0.3, 0.7], "color": "yellow"},
                {"range": [0.7, 1], "color": "red"}
            ]
        }
    ))
    st.plotly_chart(fig_gauge, use_container_width=True)
    st.markdown(
        f"<div style='color:{status_cor};font-weight:700;font-size:18px'>{status_txt}</div>",
        unsafe_allow_html=True,
    )

# ===== UI: Histórico (últimas N) =====
st.subheader(" Histórico de leituras")
hist_df = pd.DataFrame(st.session_state.hist)
st.dataframe(hist_df.tail(30), use_container_width=True)

# Avança o ponteiro para a próxima leitura (que será processada no próximo refresh)
st.session_state.idx += 1
