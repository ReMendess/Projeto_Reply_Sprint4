import streamlit as st
import joblib
import pandas as pd
import numpy as np
from sklearn.preprocessing import OrdinalEncoder
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import os

st.title("Controle das Máquinas")
INTERVALO_MS = 30_000  # 30 segundos
# Verifica se os dados simulados estão disponíveis na sessão
if "dados_simulados" not in st.session_state:
    st.error("Os dados simulados ainda não foram gerados. Acesse a página 'Monitoramento da Fábrica' primeiro.")
    st.stop()


# Carrega modelo 
modelo_path = os.path.join(os.path.dirname(__file__), "..", "model", "modelo_gb.pkl") 
modelo_path = os.path.abspath(modelo_path) 
modelo = joblib.load(modelo_path)

# Usa os dados da sessão
dados_raw = st.session_state.dados_simulados.copy()

# Mapeia Tipo e cria Tipo_Encoded
mapa_tipo = {"Baixa": "L", "Média": "M", "Alta": "H"}
dados = dados_raw.copy()
dados["Tipo"] = dados["Tipo"].map(mapa_tipo)

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
