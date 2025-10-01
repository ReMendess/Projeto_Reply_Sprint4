import streamlit as st
import pandas as pd
import joblib
import time
import plotly.graph_objects as go
from sklearn.preprocessing import OrdinalEncoder
from pathlib import Path

# ==============================
# Função para carregar modelo
# ==============================
def load_model_safely(preferred="modelo_gb.pkl"):
    from pathlib import Path

    names = [preferred, "modelo.pkl"] if preferred != "modelo.pkl" else ["modelo.pkl", "modelo_gb.pkl"]

    # Locais candidatos
    candidates = []
    for nm in names:
        candidates += [Path(nm), Path("pages") / nm, Path("model") / nm]
        if "__file__" in globals():
            candidates.append(Path(__file__).parent / nm)

    for p in candidates:
        if p and p.exists():
            m = joblib.load(p)
            st.caption(f"🔹 Modelo carregado de: `{p.as_posix()}`")
            return m

    # Busca recursiva como fallback
    for nm in names:
        found = list(Path(".").rglob(nm))
        if found:
            m = joblib.load(found[0])
            st.caption(f"🔹 Modelo carregado de: `{found[0].as_posix()}`")
            return m

    raise FileNotFoundError("❌ Modelo não encontrado. Verifique se o .pkl está no repositório/deployado.")

# ==============================
# Carregar modelo
# ==============================
modelo = load_model_safely("modelo_gb.pkl")

# ==============================
# Configuração da página
# ==============================
st.set_page_config(layout="centered")
st.title(" Monitoramento da Fábrica - Simulação com Modelo Real")

# ==============================
# Carregar dataset real
# ==============================
dados = pd.read_csv("predictive_maintenance.csv")
colunas = [
    'ID Unico', 'ID Produto', 'Tipo',
    'Temperatura do ar [K]', 'Temperatura do processo [K]',
    'Velocidade de rotação [rpm]', 'Torque [Nm]',
    'Desgaste ferramenta [min]', 'Falhou', 'Tipo de falha'
]
dados.columns = colunas

# Codificação do Tipo (L, M, H)
encoder = OrdinalEncoder(categories=[['L', 'M', 'H']])
dados['Tipo_Encoded'] = encoder.fit_transform(dados[['Tipo']])

# Features usadas no treino
features = [
    'Temperatura do ar [K]', 'Temperatura do processo [K]',
    'Velocidade de rotação [rpm]', 'Torque [Nm]',
    'Desgaste ferramenta [min]', 'Tipo_Encoded'
]

# ==============================
# Simulação em tempo real
# ==============================
INTERVALO_SEG = 30

if "idx" not in st.session_state:
    st.session_state.idx = 0

# Seleciona registro atual
registro = dados.iloc[st.session_state.idx].to_dict()

# Predição
X_registro = pd.DataFrame([registro])[features]
pred = modelo.predict(X_registro)[0]
prob = modelo.predict_proba(X_registro)[0][1]

registro["Predição"] = int(pred)
registro["Probabilidade Falha"] = round(prob, 2)

# Exibir leitura
st.markdown(f"### Última leitura (#{st.session_state.idx+1}) — atualiza a cada {INTERVALO_SEG}s")
st.json(registro)

# ==============================
# Gauge de risco
# ==============================
fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=registro["Probabilidade Falha"],
    title={'text': "Risco de Falha"},
    gauge={
        'axis': {'range': [0, 1]},
        'bar': {'color': "darkblue"},
        'steps': [
            {'range': [0, 0.3], 'color': "lightgreen"},
            {'range': [0.3, 0.7], 'color': "yellow"},
            {'range': [0.7, 1], 'color': "red"},
        ]
    }
))
st.plotly_chart(fig)

# Status textual
if registro["Probabilidade Falha"] < 0.3:
    st.success(" Normal")
elif registro["Probabilidade Falha"] < 0.7:
    st.warning(" Atenção: risco moderado de falha")
else:
    st.error(" ALERTA CRÍTICO")

# ==============================
# Visualização geral balanceada
# ==============================
falhas = dados[dados["Falhou"] == 1]
sem_falha = dados[dados["Falhou"] == 0]

qtd = st.slider(
    "Quantos registros deseja visualizar?",
    min_value=10, max_value=len(dados), value=50, step=10
)

prop_falhas = 0.3  # forçar 30% de falhas
qtd_falhas = int(qtd * prop_falhas)
qtd_sem_falha = qtd - qtd_falhas

falhas_sample = falhas.sample(min(qtd_falhas, len(falhas)), random_state=42)
sem_falha_sample = sem_falha.sample(min(qtd_sem_falha, len(sem_falha)), random_state=42)

dados_balanceados = pd.concat([falhas_sample, sem_falha_sample]).sample(frac=1, random_state=42).reset_index(drop=True)

st.subheader(f" Visualização de {qtd} registros (com mais falhas que no dataset original)")
st.dataframe(dados_balanceados, use_container_width=True)

# ==============================
# Observações por severidade
# ==============================
st.subheader(" Observações por severidade da falha")

gravidade = {
    "No Failure": " Sem falha detectada",
    "Power Failure": " Falha elétrica (grave)",
    "Tool Wear Failure": " Desgaste da ferramenta (médio)",
    "Overstrain Failure": " Sobrecarga mecânica (grave)",
    "Random Failures": " Falhas aleatórias (variável)",
    "Heat Dissipation Failure": " Problema térmico (crítico)"
}

falhas_detectadas = dados_balanceados[dados_balanceados["Falhou"] == 1].head(10)

if not falhas_detectadas.empty:
    for _, row in falhas_detectadas.iterrows():
        tipo_falha = row["Tipo de falha"]
        obs = gravidade.get(tipo_falha, " Falha não classificada")
        st.markdown(f"**ID Produto {row['ID Produto']}** → {obs}")
else:
    st.write("Nenhuma falha prevista nos registros exibidos.")

# ==============================
# Atualização do índice
# ==============================
time.sleep(1)
st.session_state.idx = (st.session_state.idx + 1) % len(dados)
st.experimental_rerun()
