
import random
import time
from random import sample

import numpy as np
import pandas as pd

def dados_wokwi(n_samples= 3000):
    np.random.seed(555)
    time.sleep(1.5)
    print("Carregando data set. . .")

    dados_temperatura = np.random.normal(loc= 27 , scale= 2,size=n_samples)
    dados_umidade = np.random.uniform(low=0, high=100,size=n_samples)
    acc_x = np.random.normal(loc=0, scale=0.3, size=n_samples)
    acc_y = np.random.normal(loc=0, scale=0.3, size=n_samples)
    acc_z = np.random.normal(loc=9.81, scale=0.4, size=n_samples)
    vibracao_total = np.sqrt(acc_x ** 2 + acc_y ** 2 + (acc_z - 9.81) ** 2)
    corrente = np.random.normal(loc= 5, scale=1.5,size=n_samples)

    df = pd.DataFrame({
        'Temperatura': dados_temperatura,
        'Umidade': dados_umidade,
        'Vibração': vibracao_total,
        'Corrente': corrente
    })
    return df


# Criando aplicação
st.title("Reply - Fase 2")
st.title("Análise Exploratória dos Dados Captados nos Sensores - Wokwi")

# Sidebar de amostras
n_samples = st.sidebar.slider("Quantidade de amostras", min_value=500, max_value=5000, value=3000, step=500)

# Botão para carregar dados
if st.sidebar.button("Gerar dados"):
    df = dados_wokwi(n_samples)

    st.success("Dados carregados!")

    # Mostrar tabela e estatísticas
    st.subheader("Dados")
    st.dataframe(df.head())

    st.subheader("Estatísticas Descritivas")
    st.write(df.describe())

    # Gráficos interativos
    st.subheader("Gráfico de Dispersão")
    x_axis = st.selectbox("Eixo X", df.columns, index=0)
    y_axis = st.selectbox("Eixo Y", df.columns, index=1)
    fig1 = px.scatter(df, x=x_axis, y=y_axis, color=df[y_axis], title=f"{y_axis} vs {x_axis}")
    st.plotly_chart(fig1)

    st.subheader("Histograma")
    hist_col = st.selectbox("Selecionar variável para histograma", df.columns, index=2)
    fig2 = px.histogram(df, x=hist_col, nbins=40, title=f"Distribuição de {hist_col}")
    st.plotly_chart(fig2)

    st.subheader("Boxplot")
    box_col = st.selectbox("Selecionar variável para boxplot", df.columns, index=3)
    fig3 = px.box(df, y=box_col, title=f"Boxplot de {box_col}")
    st.plotly_chart(fig3)

else:
    st.warning("Clique em 'Gerar dados' para iniciar a análise.")
