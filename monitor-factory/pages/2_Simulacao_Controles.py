import streamlit as st
import numpy as np
import pandas as pd
import time

st.title("Simulação de Dados e Controles")

# Controles
rpm = st.slider("RPM", 500, 5000, 1500)
temp_set = st.slider("Temperatura alvo (°C)", 20, 200, 85)

# Botões
if st.button("Gerar amostra"):
    # cria série simulada
    t = np.arange(0,60)
    vib = 0.1*np.sin(0.1*t) + (rpm/5000)*np.random.normal(0,1,len(t))
    temp = temp_set + np.random.normal(0,1,len(t))
    df = pd.DataFrame({"time":t, "rpm": rpm, "vibration": vib, "temperature": temp})
    st.session_state["sim_data"] = df
    st.success("Dados simulados gerados.")
    
if "sim_data" in st.session_state:
    st.dataframe(st.session_state["sim_data"].tail(10))
    st.line_chart(st.session_state["sim_data"].set_index("time")[["vibration","temperature"]])
