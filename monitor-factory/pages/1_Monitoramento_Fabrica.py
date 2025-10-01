import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image

st.set_page_config(layout="centered")
st.title("Monitoramento da Fábrica")

IMG_PATH = "./assets/maquinas.png"

dados = pd_read_csv("preditive_maintence.csv")

# Máquinas cadastradas
maquinas = {
    "M1": {"nome": "Torno CNC", "setor": "Usinagem", "id_produto": "M00001", "tipo": "Alta"},
    "M2": {"nome": "Prensa Hidráulica", "setor": "Montagem", "id_produto": "P00001", "tipo": "Média"},
    "M3": {"nome": "Esteira Transportadora", "setor": "Transporte", "id_produto": "E00001", "tipo": "Baixa"},
}

# Seleção fixa de máquina
sel = "M3"
info = maquinas[sel]

# Imagem da planta
planta = Image.open(IMG_PATH).resize((800, 600))
st.image(planta, caption="Layout da Fábrica", use_container_width=False)

# Informações da máquina
st.subheader(f"{info['nome']} ({sel})")
st.write(f"**Setor:** {info['setor']}")
st.write(f"**Qualidade (Tipo):** {info['tipo']}")

# Gerar dataset fixo com 800 registros
dados = criar_dados_tratados(n_samples=800, seed=int(sel[-1]))

# Sobrescrever colunas fixas
dados["ID Produto"] = info["id_produto"]
dados["Tipo"] = info["tipo"]

# Exibir dados
st.subheader("Sensores (simulação com 800 registros)")
st.dataframe(dados.head(20), use_container_width=True)

# Gráfico de linha
dados.index.name = 'Minutos'
st.line_chart(dados[["Temperatura do ar [K]", "Temperatura do processo [K]",
                     "Velocidade de rotação [rpm]", "Torque [Nm]"]].head(50))

# Armazena os dados simulados na sessão
st.session_state.dados_simulados = dados.copy()

