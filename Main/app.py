# streamlit_fim_a_fim.py
"""
Aplicação Streamlit fim-a-fim:
- Simula/recebe leituras de sensores (formulário manual ou simulação tipo ESP32)
- Ingestão para banco de dados (tenta Oracle via oracledb; em falta, usa SQLite local)
- Estruturas de tabelas criadas automaticamente (se não existirem) a partir dos scripts fornecidos
- Treina um modelo de ML (RandomForestClassifier) para identificar risco de falha
- Dashboard com painéis, gráficos e alertas inteligentes (gera registro na tabela Falha)

Configuração de conexão com Oracle:
- Use st.secrets ou variáveis de ambiente: ORACLE_USER, ORACLE_PASSWORD, ORACLE_DSN

Como usar:
- Executar: streamlit run streamlit_fim_a_fim.py
- Preencha / simule leituras, clique em Ingestão -> os dados vão ao DB
- Treine modelo com os dados existentes (botão Train)
- Veja análise, séries temporais e alertas

Observação: o comportamento de "falha" usado para rotular dados inicialmente é: leitura fora dos limites (limite_minimo/limite_maximo) -> class 1 (risco), else 0.
"""

import os
import time
from datetime import datetime
import io
import pandas as pd
import numpy as np
import streamlit as st
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
import joblib

# Tenta usar oracledb, caso contrário fallback para sqlite
USE_ORACLE = False
try:
    import oracledb
    USE_ORACLE = True
except Exception:
    USE_ORACLE = False
    import sqlite3

MODEL_PATH = "./sensor_failure_model.joblib"
DB_FALLBACK_SQLITE = "./sensor_data_local.db"

st.set_page_config(page_title="Monitoramento Industrial - Fim a Fim", layout="wide")

# ---------------------- Helpers de DB ----------------------
@st.cache_resource
def get_db_connection():
    """Retorna um objeto de conexão para Oracle ou sqlite."""
    if USE_ORACLE:
        user = st.secrets.get("ORACLE_USER") if "ORACLE_USER" in st.secrets else os.getenv("ORACLE_USER")
        password = st.secrets.get("ORACLE_PASSWORD") if "ORACLE_PASSWORD" in st.secrets else os.getenv("ORACLE_PASSWORD")
        dsn = st.secrets.get("ORACLE_DSN") if "ORACLE_DSN" in st.secrets else os.getenv("ORACLE_DSN")
        if not user or not password or not dsn:
            st.warning("oracledb disponível, mas credenciais não encontradas em st.secrets/vars de ambiente. Usando SQLite fallback.")
            conn = sqlite3.connect(DB_FALLBACK_SQLITE, check_same_thread=False)
            return ("sqlite", conn)
        try:
            conn = oracledb.connect(user=user, password=password, dsn=dsn)
            return ("oracle", conn)
        except Exception as e:
            st.error(f"Falha ao conectar Oracle: {e}. Usando SQLite fallback.")
            conn = sqlite3.connect(DB_FALLBACK_SQLITE, check_same_thread=False)
            return ("sqlite", conn)
    else:
        conn = sqlite3.connect(DB_FALLBACK_SQLITE, check_same_thread=False)
        return ("sqlite", conn)


def ensure_tables(conn_type, conn):
    """Cria as tabelas caso não existam. Use o DDL fornecido adaptado para SQLite quando necessário."""
    if conn_type == "oracle":
        cur = conn.cursor()
        # Criar tabelas usando DDL provido (com small adaptations if necessary)
        # We'll run CREATE TABLE IF NOT EXISTS style not supported by Oracle -> try/catch
        try:
            cur.execute("""
            BEGIN
            EXECUTE IMMEDIATE 'CREATE TABLE Maquinas (id_maquina NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY, nome_maquina NVARCHAR2(100) NOT NULL, qualidade_maquina NVARCHAR2(20), modelo NVARCHAR2(50), status_maquina NVARCHAR2(20) DEFAULT ''Ativa'' NOT NULL)';
            EXCEPTION WHEN OTHERS THEN
              IF SQLCODE != -955 THEN RAISE; END IF; -- ignore existing
            END;
            
            BEGIN
            EXECUTE IMMEDIATE 'CREATE TABLE Sensores (id_sensor NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY, tipo_sensor NVARCHAR2(50) NOT NULL, unidade_medida NVARCHAR2(20) NOT NULL, status_sensor NVARCHAR2(20) DEFAULT ''Ativo'' NOT NULL, limite_minimo NUMBER(10,2), limite_maximo NUMBER(10,2), id_maquina NUMBER NOT NULL)';
            EXCEPTION WHEN OTHERS THEN
              IF SQLCODE != -955 THEN RAISE; END IF;
            END;
            
            BEGIN
            EXECUTE IMMEDIATE 'CREATE TABLE Leitura_Sensor (id_leitura NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY, id_sensor NUMBER NOT NULL, data_leitura TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL, valor NUMBER(18,4) NOT NULL)';
            EXCEPTION WHEN OTHERS THEN
              IF SQLCODE != -955 THEN RAISE; END IF;
            END;
            
            BEGIN
            EXECUTE IMMEDIATE 'CREATE TABLE Falha (id_falha NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY, id_maquina NUMBER NOT NULL, id_sensor NUMBER, descricao NVARCHAR2(255) NOT NULL, nivel_severidade NVARCHAR2(20) NOT NULL, data_ocorrencia TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL, status_falha NVARCHAR2(20) DEFAULT ''Aberta'' NOT NULL)';
            EXCEPTION WHEN OTHERS THEN
              IF SQLCODE != -955 THEN RAISE; END IF;
            END;
            """)
            conn.commit()
        except Exception as e:
            st.info("Tabelas Oracle já existem ou houve erro ao criar automatico: " + str(e))
    else:
        # SQLite
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


# Funções de CRUD simples

def insert_machine(conn_type, conn, nome, qualidade='Boa', modelo=None):
    if conn_type == 'oracle':
        cur = conn.cursor()
        cur.execute("INSERT INTO Maquinas (nome_maquina, qualidade_maquina, modelo) VALUES (:1,:2,:3)", (nome,qualidade,modelo))
        conn.commit()
    else:
        cur = conn.cursor()
        cur.execute("INSERT INTO Maquinas (nome_maquina, qualidade_maquina, modelo) VALUES (?,?,?)", (nome,qualidade,modelo))
        conn.commit()


def insert_sensor(conn_type, conn, tipo, unidade, id_maquina, min_lim=None, max_lim=None):
    if conn_type == 'oracle':
        cur = conn.cursor()
        cur.execute("INSERT INTO Sensores (tipo_sensor, unidade_medida, id_maquina, limite_minimo, limite_maximo) VALUES (:1,:2,:3,:4,:5)", (tipo,unidade,id_maquina,min_lim,max_lim))
        conn.commit()
    else:
        cur = conn.cursor()
        cur.execute("INSERT INTO Sensores (tipo_sensor, unidade_medida, id_maquina, limite_minimo, limite_maximo) VALUES (?,?,?,?,?)", (tipo,unidade,id_maquina,min_lim,max_lim))
        conn.commit()


def insert_reading(conn_type, conn, id_sensor, valor, data_leitura=None):
    data_leitura = data_leitura or datetime.now()
    if conn_type == 'oracle':
        cur = conn.cursor()
        cur.execute("INSERT INTO Leitura_Sensor (id_sensor, data_leitura, valor) VALUES (:1, :2, :3)", (id_sensor, data_leitura, float(valor)))
        conn.commit()
    else:
        cur = conn.cursor()
        cur.execute("INSERT INTO Leitura_Sensor (id_sensor, data_leitura, valor) VALUES (?,?,?)", (id_sensor, data_leitura.strftime('%Y-%m-%d %H:%M:%S'), float(valor)))
        conn.commit()


def insert_failure(conn_type, conn, id_maquina, descricao, nivel='Médio', id_sensor=None):
    if conn_type == 'oracle':
        cur = conn.cursor()
        cur.execute("INSERT INTO Falha (id_maquina, id_sensor, descricao, nivel_severidade) VALUES (:1,:2,:3,:4)", (id_maquina, id_sensor, descricao, nivel))
        conn.commit()
    else:
        cur = conn.cursor()
        cur.execute("INSERT INTO Falha (id_maquina, id_sensor, descricao, nivel_severidade) VALUES (?,?,?,?)", (id_maquina, id_sensor, descricao, nivel))
        conn.commit()


def fetch_latest_readings(conn_type, conn, limit=50):
    if conn_type == 'oracle':
        q = """
        SELECT l.id_leitura, l.data_leitura, l.valor, s.tipo_sensor, s.unidade_medida, s.limite_minimo, s.limite_maximo, s.id_sensor, m.id_maquina, m.nome_maquina
        FROM Leitura_Sensor l
        JOIN Sensores s ON l.id_sensor = s.id_sensor
        JOIN Maquinas m ON s.id_maquina = m.id_maquina
        WHERE l.data_leitura IN (
            SELECT data_leitura FROM (
                SELECT data_leitura FROM Leitura_Sensor ORDER BY data_leitura DESC
            ) WHERE ROWNUM <= :1
        )
        ORDER BY l.data_leitura DESC
        """
        df = pd.read_sql(q, conn, params=(limit,))
        return df
    else:
        q = """
        SELECT l.id_leitura, l.data_leitura, l.valor, s.tipo_sensor, s.unidade_medida, s.limite_minimo, s.limite_maximo, s.id_sensor, m.id_maquina, m.nome_maquina
        FROM Leitura_Sensor l
        JOIN Sensores s ON l.id_sensor = s.id_sensor
        JOIN Maquinas m ON s.id_maquina = m.id_maquina
        ORDER BY l.data_leitura DESC LIMIT ?
        """
        df = pd.read_sql(q, conn, params=(limit,))
        return df


def fetch_all_for_ml(conn_type, conn):
    # Retorna DataFrame com features e label (label criado a partir dos limites dos sensores)
    df = fetch_latest_readings(conn_type, conn, limit=10000)
    if df.empty:
        return df
    # Criar label: 1 se valor fora dos limites e limites não nulos
    def label_row(r):
        if pd.isna(r['limite_minimo']) or pd.isna(r['limite_maximo']):
            return 0
        if (r['valor'] < r['limite_minimo']) or (r['valor'] > r['limite_maximo']):
            return 1
        return 0
    df['label'] = df.apply(label_row, axis=1)
    # Features simples: valor, distance to max/min, last hour mean for same sensor
    df['valor_minus_min'] = df.apply(lambda r: (r['valor'] - r['limite_minimo']) if not pd.isna(r['limite_minimo']) else 0, axis=1)
    df['max_minus_valor'] = df.apply(lambda r: (r['limite_maximo'] - r['valor']) if not pd.isna(r['limite_maximo']) else 0, axis=1)
    # numeric encoding for tipo_sensor
    df['tipo_sensor_code'] = pd.Categorical(df['tipo_sensor']).codes
    # timestamp
    df['data_leitura'] = pd.to_datetime(df['data_leitura'])
    df = df.sort_values('data_leitura')
    # rolling features per sensor
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

st.title("📡 Monitoramento de Sensores - Fluxo Fim-a-Fim")

conn_type, conn = get_db_connection()
ensure_tables(conn_type, conn)

# Sidebar: criação rápida de máquina/sensor
with st.sidebar.expander("Configuração rápida (Máquina / Sensor)"):
    st.subheader("Criar máquina")
    nome_maquina = st.text_input("Nome máquina", value="Maquina A")
    qualidade = st.selectbox("Qualidade", ['Ruim','Média','Boa'], index=2)
    modelo = st.text_input("Modelo", value="MD-01")
    if st.button("Criar máquina"):
        insert_machine(conn_type, conn, nome_maquina, qualidade, modelo)
        st.success("Máquina criada")
    st.markdown("---")
    st.subheader("Criar sensor")
    tipo_sensor = st.text_input("Tipo sensor", value="Temperatura")
    unidade = st.text_input("Unidade", value="C")
    id_maquina_input = st.number_input("ID Máquina (ex: 1)", min_value=1, value=1)
    min_lim = st.number_input("Limite mínimo (ou 0)", value=0.0, format="%f")
    max_lim = st.number_input("Limite máximo (ou 100)", value=100.0, format="%f")
    if st.button("Criar sensor"):
        try:
            insert_sensor(conn_type, conn, tipo_sensor, unidade, id_maquina_input, min_lim, max_lim)
            st.success("Sensor criado")
        except Exception as e:
            st.error(f"Erro ao criar sensor: {e}")

st.markdown("# Ingestão de Leituras")
col1, col2 = st.columns([2,1])

with col1:
    st.subheader("Inserir leitura (manual / simulação)")
    # Buscar sensores existentes
    try:
        sensors_df = pd.read_sql('SELECT id_sensor, tipo_sensor, unidade_medida, limite_minimo, limite_maximo, id_maquina FROM Sensores', conn)
    except Exception:
        try:
            sensors_df = pd.read_sql('SELECT id_sensor, tipo_sensor, unidade_medida, limite_minimo, limite_maximo, id_maquina FROM Sensores', conn)
        except Exception:
            sensors_df = pd.DataFrame(columns=['id_sensor','tipo_sensor','unidade_medida','limite_minimo','limite_maximo','id_maquina'])

    if sensors_df.empty:
        st.info("Nenhum sensor cadastrado. Cadastre um sensor no menu lateral.")
    else:
        sid = st.selectbox("Escolher sensor", sensors_df['id_sensor'].astype(str) + ' - ' + sensors_df['tipo_sensor'], index=0)
        sid_int = int(sid.split(' - ')[0])
        val = st.number_input("Valor leitura", value=float(sensors_df.loc[sensors_df['id_sensor']==sid_int,'limite_minimo'].fillna(0).values[0] + 1 if not sensors_df.empty else 0))
        if st.button("Inserir leitura no DB"):
            try:
                insert_reading(conn_type, conn, sid_int, val)
                st.success("Leitura inserida")
            except Exception as e:
                st.error(f"Erro ao inserir leitura: {e}")

        st.markdown("---")
        st.subheader("Simular leituras automáticas (ESP32)")
        num = st.number_input("Quantas leituras (rápido)", min_value=1, max_value=500, value=10)
        if st.button("Simular e inserir"):
            n = int(num)
            inserted = 0
            for i in range(n):
                # gerar valor aleatório dentro de uma faixa +/-25% do range ou do próprio limite
                row = sensors_df[sensors_df['id_sensor']==sid_int].iloc[0]
                lo = row['limite_minimo'] if not pd.isna(row['limite_minimo']) else 0
                hi = row['limite_maximo'] if not pd.isna(row['limite_maximo']) else lo + 100
                jitter = np.random.normal(loc=0, scale=(hi-lo+1)/8)
                v = float(np.clip((hi+lo)/2 + jitter, lo - (hi-lo)*0.5, hi + (hi-lo)*0.5))
                insert_reading(conn_type, conn, sid_int, v)
                inserted += 1
            st.success(f"{inserted} leituras simuladas inseridas")

with col2:
    st.subheader("Últimas leituras")
    latest = fetch_latest_readings(conn_type, conn, limit=50)
    if latest.empty:
        st.write("Sem leituras ainda")
    else:
        st.dataframe(latest)

st.markdown("# Treinamento do Modelo de ML")
ml_col1, ml_col2 = st.columns([2,1])
with ml_col1:
    df_ml = fetch_all_for_ml(conn_type, conn)
    st.write(f"Registros disponíveis para ML: {0 if df_ml is None else len(df_ml)}")
    if df_ml is not None and not df_ml.empty:
        st.dataframe(df_ml.head(200))
    if st.button("Treinar modelo com os dados atuais"):
        with st.spinner("Treinando..."):
            model, metrics = train_model(df_ml)
            if model is not None:
                joblib.dump(model, MODEL_PATH)
                st.success("Modelo treinado e salvo")
                st.metric("AUC", value=(round(metrics['auc'],3) if metrics['auc'] is not None else 'n/a'))
                st.write(pd.DataFrame(metrics['report']).transpose())

with ml_col2:
    st.subheader("Gerenciar modelo")
    loaded = load_model()
    if loaded is not None:
        st.success("Modelo encontrado e carregado")
        if st.button("Excluir modelo salvo"):
            try:
                os.remove(MODEL_PATH)
                st.success("Modelo removido")
            except Exception as e:
                st.error(f"Erro ao apagar: {e}")
    else:
        st.info("Nenhum modelo salvo. Treine um modelo usando os dados (botão).")

st.markdown("# Análise e Dashboard")

# Visualization per sensor
sensors = pd.read_sql('SELECT id_sensor, tipo_sensor, unidade_medida, limite_minimo, limite_maximo, id_maquina FROM Sensores', conn)
if sensors.empty:
    st.info("Sem sensores para análise. Cadastre sensores no menu lateral.")
else:
    sel = st.selectbox("Sensor para análise", sensors['id_sensor'].astype(str) + ' - ' + sensors['tipo_sensor'])
    sel_id = int(sel.split(' - ')[0])
    # fetch all readings for sensor
    q = "SELECT l.id_leitura, l.data_leitura, l.valor FROM Leitura_Sensor l WHERE l.id_sensor = ? ORDER BY l.data_leitura DESC LIMIT 500" if conn_type=='sqlite' else "SELECT l.id_leitura, l.data_leitura, l.valor FROM Leitura_Sensor l WHERE l.id_sensor = :1 ORDER BY l.data_leitura DESC"
    try:
        if conn_type=='sqlite':
            df_sensor = pd.read_sql(q, conn, params=(sel_id,))
        else:
            df_sensor = pd.read_sql(q, conn, params=(sel_id,))
        df_sensor['data_leitura'] = pd.to_datetime(df_sensor['data_leitura'])
        df_sensor = df_sensor.sort_values('data_leitura')
        st.line_chart(df_sensor.set_index('data_leitura')['valor'])
        st.dataframe(df_sensor.tail(50))
    except Exception as e:
        st.error(f"Erro ao buscar leituras do sensor: {e}")

# Real-time scoring of last reading
st.markdown("---")
st.subheader("Scoring / Alertas")
model = load_model()
latest_one = fetch_latest_readings(conn_type, conn, limit=1)
if latest_one.empty:
    st.info("Sem leituras para pontuar")
else:
    r = latest_one.iloc[0]
    st.write("Última leitura:")
    st.json(r.to_dict())
    if model is not None:
        # construct feature vector same as train
        sample = pd.DataFrame([{
            'valor': r['valor'],
            'valor_minus_min': (r['valor'] - r['limite_minimo']) if not pd.isna(r['limite_minimo']) else 0,
            'max_minus_valor': (r['limite_maximo'] - r['valor']) if not pd.isna(r['limite_maximo']) else 0,
            'tipo_sensor_code': 0,
            'valor_rolling_mean_5': r['valor'],
            'valor_rolling_std_5': 0
        }])
        # encode tipo_sensor
        try:
            # get mapping from training? we used categorical codes; this is a simplification
            sample['tipo_sensor_code'] = pd.Categorical([r['tipo_sensor']]).codes
        except Exception:
            sample['tipo_sensor_code'] = 0
        prob = model.predict_proba(sample)[0][1] if hasattr(model, 'predict_proba') else None
        pred = model.predict(sample)[0]
        st.write(f"Probabilidade de risco de falha: {prob:.3f}" if prob is not None else f"Predito: {pred}")
        alert_thresh = st.slider("Threshold para alertar (probabilidade)", 0.0, 1.0, 0.5)
        if prob is not None and prob >= alert_thresh:
            st.error(f"ALERTA: risco alto detectado (p={prob:.3f}). Gerando registro de Falha.")
            if st.button("Registrar Falha no DB"):
                try:
                    # pegar maquina id
                    id_maquina = int(r['id_maquina']) if 'id_maquina' in r else None
                    insert_failure(conn_type, conn, id_maquina, f"Alerta automático: prob {prob:.3f}", nivel='Alto', id_sensor=int(r['id_sensor']))
                    st.success("Falha registrada")
                except Exception as e:
                    st.error(f"Erro ao inserir falha: {e}")
        else:
            if prob is not None:
                st.success(f"Sem alerta - probabilidade {prob:.3f} abaixo do limiar {alert_thresh}")
            else:
                st.info("Modelo não fornece probabilidade; exibindo rótulo")

st.markdown("\n\n---\nAplicação criada para demonstração. Ajuste thresholds, features e pipelines para um cenário de produção.")

