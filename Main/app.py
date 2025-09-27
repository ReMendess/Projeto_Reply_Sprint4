# streamlit_fim_a_fim.py
"""
Aplicação Streamlit fim-a-fim (versão adaptada para Streamlit Cloud):
- Usa apenas SQLite local (Oracle removido para compatibilidade online)
- Cria tabelas automaticamente se não existirem
- Simula/inserir leituras de sensores
- Treina RandomForestClassifier para prever risco de falha
- Dashboard com análise, gráficos e alertas
"""

import os
from datetime import datetime
import pandas as pd
import numpy as np
import streamlit as st
import sqlite3
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
import joblib

# ---------------------- Config ----------------------
DB_FILE = "sensor_data_local.db"
MODEL_PATH = "sensor_model.pkl"

def get_connection():
    """Retorna conexão SQLite (sempre disponível no Streamlit Cloud)."""
    return sqlite3.connect(DB_FILE, check_same_thread=False)

# ---------------------- Helpers DB ----------------------
def ensure_tables(conn):
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS Maquinas (
        id_maquina INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_maquina TEXT NOT NULL,
        qualidade_maquina TEXT,
        modelo TEXT,
        status_maquina TEXT DEFAULT 'Ativa' NOT NULL
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS Sensores (
        id_sensor INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo_sensor TEXT NOT NULL,
        unidade_medida TEXT NOT NULL,
        status_sensor TEXT DEFAULT 'Ativo' NOT NULL,
        limite_minimo REAL,
        limite_maximo REAL,
        id_maquina INTEGER NOT NULL,
        FOREIGN KEY (id_maquina) REFERENCES Maquinas(id_maquina) ON DELETE CASCADE
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS Leitura_Sensor (
        id_leitura INTEGER PRIMARY KEY AUTOINCREMENT,
        id_sensor INTEGER NOT NULL,
        data_leitura TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
        valor REAL NOT NULL,
        FOREIGN KEY (id_sensor) REFERENCES Sensores(id_sensor) ON DELETE CASCADE
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS Falha (
        id_falha INTEGER PRIMARY KEY AUTOINCREMENT,
        id_maquina INTEGER NOT NULL,
        id_sensor INTEGER,
        descricao TEXT NOT NULL,
        nivel_severidade TEXT NOT NULL,
        data_ocorrencia TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
        status_falha TEXT DEFAULT 'Aberta' NOT NULL
    );
    """)
    conn.commit()

def clear_readings(conn):
    cur = conn.cursor()
    cur.execute("DELETE FROM Leitura_Sensor")
    conn.commit()

def insert_machine(conn, nome, qualidade='Boa', modelo=None):
    cur = conn.cursor()
    cur.execute("INSERT INTO Maquinas (nome_maquina, qualidade_maquina, modelo) VALUES (?,?,?)",
                (nome, qualidade, modelo))
    conn.commit()

def insert_sensor(conn, tipo, unidade, id_maquina, min_lim=None, max_lim=None):
    cur = conn.cursor()
    cur.execute("INSERT INTO Sensores (tipo_sensor, unidade_medida, id_maquina, limite_minimo, limite_maximo) VALUES (?,?,?,?,?)",
                (tipo, unidade, id_maquina, min_lim, max_lim))
    conn.commit()

def insert_reading(conn, id_sensor, valor, data_leitura=None):
    data_leitura = data_leitura or datetime.now()
    cur = conn.cursor()
    cur.execute("INSERT INTO Leitura_Sensor (id_sensor, data_leitura, valor) VALUES (?,?,?)",
                (id_sensor, data_leitura.strftime('%Y-%m-%d %H:%M:%S'), float(valor)))
    conn.commit()

def insert_failure(conn, id_maquina, descricao, nivel='Médio', id_sensor=None):
    cur = conn.cursor()
    cur.execute("INSERT INTO Falha (id_maquina, id_sensor, descricao, nivel_severidade) VALUES (?,?,?,?)",
                (id_maquina, id_sensor, descricao, nivel))
    conn.commit()

def fetch_latest_readings(conn, limit=50):
    q = """
    SELECT l.id_leitura, l.data_leitura, l.valor,
           s.tipo_sensor, s.unidade_medida, s.limite_minimo, s.limite_maximo,
           s.id_sensor, m.id_maquina, m.nome_maquina
    FROM Leitura_Sensor l
    JOIN Sensores s ON l.id_sensor = s.id_sensor
    JOIN Maquinas m ON s.id_maquina = m.id_maquina
    ORDER BY l.data_leitura DESC LIMIT ?
    """
    return pd.read_sql(q, conn, params=(limit,))

def fetch_all_for_ml(conn):
    df = fetch_latest_readings(conn, limit=10000)
    if df.empty:
        return df
    def label_row(r):
        if pd.isna(r['limite_minimo']) or pd.isna(r['limite_maximo']):
            return 0
        return 1 if (r['valor'] < r['limite_minimo']) or (r['valor'] > r['limite_maximo']) else 0
    df['label'] = df.apply(label_row, axis=1)
    df['valor_minus_min'] = df.apply(lambda r: (r['valor'] - r['limite_minimo']) if not pd.isna(r['limite_minimo']) else 0, axis=1)
    df['max_minus_valor'] = df.apply(lambda r: (r['limite_maximo'] - r['valor']) if not pd.isna(r['limite_maximo']) else 0, axis=1)
    df['tipo_sensor_code'] = pd.Categorical(df['tipo_sensor']).codes
    df['data_leitura'] = pd.to_datetime(df['data_leitura'])
    df = df.sort_values('data_leitura')
    df['valor_rolling_mean_5'] = df.groupby('id_sensor')['valor'].rolling(5, min_periods=1).mean().reset_index(0,drop=True)
    df['valor_rolling_std_5'] = df.groupby('id_sensor')['valor'].rolling(5, min_periods=1).std().reset_index(0,drop=True).fillna(0)
    return df

# ---------------------- ML ----------------------
def train_model(df):
    if df.empty:
        st.warning("Sem dados para treinar")
        return None, None
    features = ['valor', 'valor_minus_min', 'max_minus_valor', 'tipo_sensor_code', 'valor_rolling_mean_5', 'valor_rolling_std_5']
    X = df[features].fillna(0)
    y = df['label']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y if len(y.unique())>1 else None)
    pipe = Pipeline([('scaler', StandardScaler()), ('clf', RandomForestClassifier(n_estimators=100, random_state=42))])
    pipe.fit(X_train, y_train)
    preds = pipe.predict(X_test)
    proba = pipe.predict_proba(X_test)[:,1] if hasattr(pipe, 'predict_proba') else None
    report = classification_report(y_test, preds, output_dict=True, zero_division=0)
    auc = roc_auc_score(y_test, proba) if proba is not None and len(np.unique(y_test))>1 else None
    return pipe, {'report':report, 'auc':auc}

def load_model():
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)
    return None

# ---------------------- UI ----------------------
st.title("📡 Monitoramento de Sensores - Fim-a-Fim")

conn = get_connection()
ensure_tables(conn)

# --- Sidebar para cadastro ---
with st.sidebar.expander("⚙️ Configuração rápida"):
    st.subheader("Criar máquina")
    nome_maquina = st.text_input("Nome máquina", value="Maquina A")
    qualidade = st.selectbox("Qualidade", ['Ruim','Média','Boa'], index=2)
    modelo = st.text_input("Modelo", value="MD-01")
    if st.button("Criar máquina"):
        insert_machine(conn, nome_maquina, qualidade, modelo)
        st.success("Máquina criada")

    st.subheader("Criar sensor")
    tipo_sensor = st.text_input("Tipo sensor", value="Temperatura")
    unidade = st.text_input("Unidade", value="C")
    id_maquina_input = st.number_input("ID Máquina", min_value=1, value=1)
    min_lim = st.number_input("Limite mínimo", value=0.0, format="%f")
    max_lim = st.number_input("Limite máximo", value=100.0, format="%f")
    if st.button("Criar sensor"):
        insert_sensor(conn, tipo_sensor, unidade, id_maquina_input, min_lim, max_lim)
        st.success("Sensor criado")

# --- Ingestão ---
st.header("📥 Ingestão de Leituras")
sensors_df = pd.read_sql('SELECT * FROM Sensores', conn)
if sensors_df.empty:
    st.info("Nenhum sensor cadastrado.")
else:
    sid = st.selectbox("Escolher sensor", sensors_df['id_sensor'].astype(str) + ' - ' + sensors_df['tipo_sensor'])
    sid_int = int(sid.split(' - ')[0])
    val = st.number_input("Valor leitura", value=10.0)
    if st.button("Inserir leitura"):
        insert_reading(conn, sid_int, val)
        st.success("Leitura inserida")

    if st.button("Simular 10 leituras"):
        row = sensors_df[sensors_df['id_sensor']==sid_int].iloc[0]
        lo, hi = row['limite_minimo'] or 0, row['limite_maximo'] or 100
        for _ in range(10):
            jitter = np.random.normal(loc=0, scale=(hi-lo+1)/8)
            v = float(np.clip((hi+lo)/2 + jitter, lo-(hi-lo)*0.5, hi+(hi-lo)*0.5))
            insert_reading(conn, sid_int, v)
        st.success("10 leituras simuladas")

latest = fetch_latest_readings(conn, limit=20)
st.subheader("Últimas leituras")
st.dataframe(latest)

if st.button("🗑️ Limpar todas as leituras"):
    clear_readings(conn)
    st.success("Todas as leituras foram removidas.")

# --- Treinamento ---
st.header("🤖 Treinamento do Modelo")
df_ml = fetch_all_for_ml(conn)
st.write(f"Registros disponíveis: {len(df_ml)}")
if st.button("Treinar modelo"):
    model, metrics = train_model(df_ml)
    if model:
        joblib.dump(model, MODEL_PATH)
        st.success("Modelo treinado e salvo")
        st.metric("AUC", value=metrics['auc'])
        st.write(pd.DataFrame(metrics['report']).transpose())

# --- Análise ---
st.header("📊 Dashboard")
if not sensors_df.empty:
    sel = st.selectbox("Sensor para análise", sensors_df['id_sensor'].astype(str) + ' - ' + sensors_df['tipo_sensor'])
    sel_id = int(sel.split(' - ')[0])
    q = "SELECT * FROM Leitura_Sensor WHERE id_sensor=? ORDER BY data_leitura DESC LIMIT 200"
    df_sensor = pd.read_sql(q, conn, params=(sel_id,))
    df_sensor['data_leitura'] = pd.to_datetime(df_sensor['data_leitura'])
    df_sensor = df_sensor.sort_values('data_leitura')
    st.line_chart(df_sensor.set_index('data_leitura')['valor'])
    st.dataframe(df_sensor.tail(20))

# --- Scoring ---
st.header("🚨 Scoring / Alertas")
model = load_model()
latest_one = fetch_latest_readings(conn, limit=1)
if not latest_one.empty and model is not None:
    r = latest_one.iloc[0]
    sample = pd.DataFrame([{
        'valor': r['valor'],
        'valor_minus_min': (r['valor'] - r['limite_minimo']) if not pd.isna(r['limite_minimo']) else 0,
        'max_minus_valor': (r['limite_maximo'] - r['valor']) if not pd.isna(r['limite_maximo']) else 0,
        'tipo_sensor_code': pd.Categorical([r['tipo_sensor']]).codes[0],
        'valor_rolling_mean_5': r['valor'],
        'valor_rolling_std_5': 0
    }])
    prob = model.predict_proba(sample)[0][1]
    st.write(f"Probabilidade de falha: {prob:.2f}")
    if prob > 0.5:
        st.error("⚠️ ALERTA: risco alto detectado!")
else:
    st.info("Sem leituras ou modelo ainda não treinado.")

st.markdown("---\nAplicação demo para Streamlit Cloud")
