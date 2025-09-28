import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image

st.set_page_config(layout="centered")
st.title(" Fábrica Interativa — ")

IMG_PATH = "./assets/maquinas.png"

# --------- Função original ---------
def criar_dados_tratados(n_samples=5000, seed=42):
    np.random.seed(seed)

    id_unico = np.arange(1, n_samples + 1)
    id_produto = [f"M{id:05d}" if np.random.rand() < 0.5 else f"L{id:05d}" for id in id_unico]
    tipo = ["M" if p.startswith("M") else "L" for p in id_produto]

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

# --------- Máquinas pré-cadastradas ---------
maquinas = {
    "M1": {"nome": "Torno CNC", "setor": "Usinagem", "id_produto": "M00001", "tipo": "Alta"},
    "M2": {"nome": "Prensa Hidráulica", "setor": "Montagem", "id_produto": "P00001", "tipo": "Média"},
    "M3": {"nome": "Esteira Transportadora", "setor": "Transporte", "id_produto": "E00001", "tipo": "Baixa"},
}

# --------- Menu lateral ---------
sel = st.sidebar.radio("Selecione a máquina:", list(maquinas.keys()))
n_dados = st.sidebar.slider("Quantos dados deseja gerar?", min_value=10, max_value=1000, value=200, step=10)

info = maquinas[sel]

# --------- Mostrar planta ---------
planta = Image.open(IMG_PATH).resize((380, 380))
st.image(planta, caption="Layout da Fábrica", use_container_width=False)

# --------- Info da máquina ---------
st.subheader(f"📌 {info['nome']} ({sel})")
st.write(f"**Setor:** {info['setor']}")
st.write(f"**Qualidade (Tipo):** {info['tipo']}")

# --------- Gerar dataset ---------
dados = criar_dados_tratados(n_samples=n_dados, seed=int(sel[-1]))

# Sobrescrevendo as colunas fixas
dados["ID Produto"] = info["id_produto"]
dados["Tipo"] = info["tipo"]

st.subheader(f" Sensores (simulação com {n_dados} registros)")
st.dataframe(dados.head(20), use_container_width=True)

# --------- Download + gráfico ---------
csv = dados.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Baixar CSV", data=csv, file_name=f"{sel}_sensores.csv", mime="text/csv")

st.line_chart(dados[["Temperatura do ar [K]", "Temperatura do processo [K]",
                     "Velocidade de rotação [rpm]", "Torque [Nm]"]].head(50), index = 'Segundos')
