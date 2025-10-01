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
    tipo = ["Alta"] * n_samples

    temp_ar = np.random.normal(loc=298, scale=1, size=n_samples)
    temp_proc = np.random.normal(loc=308, scale=2, size=n_samples)
    rotacao = np.random.normal(loc=1500, scale=100, size=n_samples)
    torque = np.random.normal(loc=40, scale=5, size=n_samples)
    desgaste = np.clip(np.random.randint(0, 240, size=n_samples), 0, 240)

    falhou = np.random.choice([0, 1], size=n_samples, p=[0.9, 0.1])
    tipos_falha = ["No Failure", "Power Failure", "Tool Wear Failure", "Overstrain Failure", "Random Failure"]
    tipo_falha = [np.random.choice(tipos_falha) if f == 1 else "No Failure" for f in falhou]

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

# Botão de reset
cols_top = st.columns([1, 1, 3])
with cols_top[0]:
    if st.button("Reset simulação"):
        st.session_state.idx = 0
        st.session_state.hist = []
        st.rerun()

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
