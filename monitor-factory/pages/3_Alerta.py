import streamlit as st
import pandas as pd
import numpy as np
import time
import requests


## CONFIG EvolutionAPI
API_URL = "http://localhost:8080"
API_KEY = "pwd159753"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}
client = Client(ACCOUNT_SID, AUTH_TOKEN)

# ==============================
# Função para simular leitura
# ==============================
def gerar_leitura(id_unico=1, id_produto=101, tipo="A"):
    temp_ar = np.random.uniform(290, 320)  # K
    temp_proc = np.random.uniform(300, 350)
    rotacao = np.random.uniform(1000, 3000)
    torque = np.random.uniform(20, 100)
    desgaste = np.random.uniform(0, 200)
    falhou = 0
    tipo_falha = "Nenhuma"

    df = pd.DataFrame({
        "ID Unico": [id_unico],
        "ID Produto": [id_produto],
        "Tipo": [tipo],
        "Temperatura do ar [K]": [temp_ar],
        "Temperatura do processo [K]": [temp_proc],
        "Velocidade de rotação [rpm]": [rotacao],
        "Torque [Nm]": [torque],
        "Desgaste ferramenta [min]": [desgaste],
        "Falhou": [falhou],
        "Tipo de falha": [tipo_falha]
    })
    return df

# ==============================
# Modelo (simulação de risco)
# ==============================
def modelo_predicao(df):
    risco = "Baixo"
    if df["Temperatura do processo [K]"].iloc[0] > 340 or df["Desgaste ferramenta [min]"].iloc[0] > 180:
        risco = "Alto"
    elif df["Torque [Nm]"].iloc[0] > 90:
        risco = "Médio"
    return risco

def enviarEvolution(numero, mensagem):
    try:
        payload = {
            "to": numero,  # precisa ser no formato 5511999999999
            "text": mensagem
        }
        resp = requests.post(f"{API_URL}/message/sendText/{INSTANCE}",
                             headers=HEADERS, json=payload)
        if resp.status_code == 200:
            st.success(f"Mensagem enviada ao operador!")
        else:
            st.error(f"Erro ao enviar mensagem: {resp.text}")
    except Exception as e:
        st.error(f"Erro de conexão com Evolution API: {e}")
# ==============================
# Interface Streamlit
# ==============================
st.title("Monitoramento de Sensores - Alertas")

numero_whats = st.text_input("Insira o número do WhatsApp do operador (com DDI, ex: 5511999999999)")

st.sidebar.header("Manipular sensores")
forcar_falha = st.sidebar.checkbox("Forçar falha")
temp_proc_forcado = st.sidebar.slider("Temperatura do processo [K]", 300, 400, 320)
desgaste_forcado = st.sidebar.slider("Desgaste ferramenta [min]", 0, 250, 100)

start = st.button("▶️ Iniciar Monitoramento")

if start:
    placeholder = st.empty()
    while True:
        leitura = gerar_leitura()

        # Se usuário forçar falha, sobrescreve valores
        if forcar_falha:
            leitura["Temperatura do processo [K]"] = temp_proc_forcado
            leitura["Desgaste ferramenta [min]"] = desgaste_forcado

        risco = modelo_predicao(leitura)

        placeholder.write(leitura)
        st.write(f" Risco identificado: **{risco}**")

        if risco == "Alto" and numero_whats:
            enviarEvolution(numero_whats, f" Alerta: Alto risco de falha detectado!")

        time.sleep(20)  # simula a cada 20s
