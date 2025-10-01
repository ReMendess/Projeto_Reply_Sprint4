import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
from sklearn.preprocessing import OrdinalEncoder

st.set_page_config(layout="centered")
st.title("Monitoramento da Fábrica")

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
# 🔹 Ordenar para trazer falhas primeiro
dados_ordenados = dados.sort_values(by="Falhou", ascending=False).reset_index(drop=True)

# 🔹 Slider para escolher quantos registros exibir
qtd = st.slider("Quantos registros deseja exibir?", min_value=5, max_value=len(dados_ordenados), value=20, step=5)

# Exibir tabela
st.subheader(f"Exibindo os {qtd} primeiros registros (falhas primeiro)")
st.dataframe(dados_ordenados.head(qtd), use_container_width=True)

# Gráfico baseado nos mesmos registros
st.line_chart(dados_ordenados[["Temperatura do ar [K]", 
                               "Temperatura do processo [K]", 
                               "Velocidade de rotação [rpm]", 
                               "Torque [Nm]"]].head(qtd))
