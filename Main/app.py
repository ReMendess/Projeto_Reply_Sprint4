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

def insert_machine(conn, nome, qualidade='Boa', modelo=None):
    cur = conn.cursor()
    cur.execute("INSERT INTO Maquinas (nome_maquina, qualidade_maquina
