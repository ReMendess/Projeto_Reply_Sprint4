import streamlit as st
import joblib
import pandas as pd
import numpy as np
from sklearn.preprocessing import OrdinalEncoder
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import os

st.title("Controle das Máquinas")

# Função para gerar dados simulados
def criar_dados_tratados(n_samples=800, seed=42):
    np.random.seed(seed)
    id_unico = np.arange(1, n_samples + 1)
    id_produto = ["M00001"] * n_samples
    tipo = np.random.choice(["Baixa", "Média", "Alta"], size=n_samples, p=[0.2, 0.3, 0.5])

    # Ciclo operacional simulando desgaste progressivo
    ciclo_operacional = np.linspace(0, 1, n_samples)
    desgaste = np.clip((ciclo_operacional * 300 + np.random.normal(0, 15, n_samples)).astype(int), 0, 240)

    # Sensores com ruído e eventos anômalos
    temp_ar = np.random.normal(loc=298, scale=1, size=n_samples)
    temp_proc = np.random.normal(loc=308, scale=2, size=n_samples)
    rotacao = np.random.normal(loc=1500, scale=100, size=n_samples)
    torque = np.random.normal(loc=40, scale=5, size=n_samples)

    # Eventos críticos: aumento de temperatura e torque com desgaste alto
    temp_proc += np.where(desgaste > 180, np.random.normal(5, 2, n_samples), 0)
    torque += np.where(desgaste > 180, np.random.normal(10, 3, n_samples), 0)

    # Probabilidade de falha baseada em desgaste
    prob_falha = np.interp(desgaste, [0, 240], [0.05, 0.9])
    falhou = np.random.binomial(1, prob_falha)

    # Tipos de falha correlacionados com sensores
    tipos_falha = ["No Failure", "Power Failure", "Tool Wear Failure", "Overstrain Failure", "Random Failure"]
    tipo_falha = []
    for i in range(n_samples):
        if falhou[i]:
            if temp_proc[i] > 312 and torque[i] > 55:
                tipo_falha.append("Overstrain Failure")
            elif desgaste[i] > 200:
                tipo_falha.append("Tool Wear Failure")
            elif rotacao[i] > 1600:
                tipo_falha.append("Power Failure")
            else:
                tipo_falha.append("Random Failure")
        else:
            tipo_falha.append("No Failure")

    df = pd.DataFrame({
        "ID Unico": id_unico,
        "ID Produto": id_produto,
        "Tipo": tipo,
        "Temperatura do ar [K]": temp_ar,
        "Temperatura do processo [K]": temp_proc,
        "Velocidade de rotação [rpm]": rotacao,
        "Torque [Nm]": torque,
        "Desgaste ferramenta [min]": desgaste,
        "Falhou": falhou,
        "Tipo de falha": tipo_falha
    })
    return df

#intervalo
INTERVALO_MS = 5_000

if "idx" not in st.session_state:
    st.session_state.idx = 0
if "hist" not in st.session_state:
    st.session_state.hist = []

# Carrega modelo
modelo_path = os.path.join(os.path.dirname(__file__), "..", "model", "modelo_gb.pkl")
modelo_path = os.path.abspath(modelo_path)
modelo = joblib.load(modelo_path)

# Gera dados simulados
dados_raw = criar_dados_tratados(n_samples=800, seed=42)

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
    st.success("Fim do arquivo — todas as leituras foram processadas.")
    if st.session_state.hist:
        st.dataframe(pd.DataFrame(st.session_state.hist))
    st.stop()

# ===== Tick (a cada 30s) =====
# Atualiza o app a cada 30s automaticamente
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
    "Leitura": int(i + 1),
    **{k: (dados_raw.iloc[i][k].item() if hasattr(dados_raw.iloc[i][k], "item") else dados_raw.iloc[i][k])
       for k in dados_raw.columns},
    "Predição": int(y_pred),
    "Probabilidade Falha": float(round(y_proba, 3))
}

st.session_state.hist.append(registro)

# ===== UI: Última leitura =====
st.subheader(f" Última leitura (#{i+1}) — atualiza a cada 30s")
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
