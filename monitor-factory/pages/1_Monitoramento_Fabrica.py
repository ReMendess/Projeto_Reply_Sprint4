import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
from sklearn.preprocessing import OrdinalEncoder

st.set_page_config(layout="centered")
st.title("Monitoramento da Fábrica")

# Caminho da imagem da planta
IMG_PATH = "./assets/maquinas.png"

# ----------------------------
# Carregar dados
dados = pd.read_csv("predictive_maintenance.csv")
colunas = ['ID Unico', 'ID Produto', 'Tipo', 'Temperatura do ar [K]', 
           'Temperatura do processo [K]', 'Velocidade de rotação [rpm]', 
           'Torque [Nm]', 'Desgaste ferramenta [min]', 'Falhou','Tipo de falha']
dados.columns = colunas

# Remover colunas inúteis
X = dados.drop(['ID Produto', 'ID Unico'], axis=1)

# Criar cópia para evitar warnings
dados_novos = X[X['Velocidade de rotação [rpm]'] < 2750].copy()

# Encodar corretamente (L/M/H)
encoder = OrdinalEncoder(categories=[['L','M','H']])
dados_novos['Tipo_Encoded'] = encoder.fit_transform(dados_novos[['Tipo']])
dados_novos = dados_novos.drop(['Tipo'], axis=1)

# ----------------------------
# Máquinas cadastradas
maquinas = {
    "M1": {"nome": "Torno CNC", "setor": "Usinagem", "id_produto": "M00001", "tipo": "H"},
    "M2": {"nome": "Prensa Hidráulica", "setor": "Montagem", "id_produto": "P00001", "tipo": "M"},
    "M3": {"nome": "Esteira Transportadora", "setor": "Transporte", "id_produto": "E00001", "tipo": "L"},
}

# Seleção fixa de máquina
sel = "M3"
info = maquinas[sel]

# Imagem da planta
planta = Image.open(IMG_PATH).resize((800, 600))
st.image(planta, caption="Layout da Fábrica")

# Informações da máquina
st.subheader(f"{info['nome']} ({sel})")
st.write(f"**Setor:** {info['setor']}")
st.write(f"**Qualidade (Tipo):** {info['tipo']}")

# ----------------------------
# Oversampling visual das falhas
falhas = dados[dados["Falhou"] == 1]
sem_falha = dados[dados["Falhou"] == 0]

# Slider para quantidade de registros
qtd = st.slider("Quantos registros deseja exibir?", 
                min_value=10, max_value=len(dados), value=50, step=10)

# Proporção de falhas exibidas
prop_falhas = 0.2  # 30% dos registros exibidos serão falhas
qtd_falhas = int(qtd * prop_falhas)
qtd_sem_falha = qtd - qtd_falhas

# Amostrar
falhas_sample = falhas.sample(min(qtd_falhas, len(falhas)), random_state=42)
sem_falha_sample = sem_falha.sample(min(qtd_sem_falha, len(sem_falha)), random_state=42)

# Concatenar e embaralhar
dados_balanceados = pd.concat([falhas_sample, sem_falha_sample]).sample(frac=1, random_state=42).reset_index(drop=True)

# ----------------------------
# Exibir tabela balanceada
st.subheader(f"Exibindo {qtd} registros (mais falhas que no dataset original)")
st.dataframe(dados_balanceados, use_container_width=True)

# Gráfico baseado nos mesmos registros
st.line_chart(dados_balanceados[["Temperatura do ar [K]", 
                                 "Temperatura do processo [K]", 
                                 "Velocidade de rotação [rpm]", 
                                 "Torque [Nm]"]])

# ----------------------------
# Armazenar dados simulados na sessão
st.session_state.dados_simulados = dados_balanceados.copy()
