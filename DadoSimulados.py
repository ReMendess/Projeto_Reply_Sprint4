import numpy as np
import pandas as pd

def criar_dados_tratados(n_samples=5000, seed=42):
    np.random.seed(seed)

    # IDs artificiais
    id_unico = np.arange(1, n_samples + 1)
    id_produto = [f"M{id:05d}" if np.random.rand() < 0.5 else f"L{id:05d}" for id in id_unico]
    tipo = ["M" if p.startswith("M") else "L" for p in id_produto]

    # Variáveis contínuas (baseadas em ranges realistas do dataset)
    temp_ar = np.random.normal(loc=298, scale=1, size=n_samples)  # ~25°C
    temp_proc = np.random.normal(loc=308, scale=2, size=n_samples)  # ~35°C
    rotacao = np.random.normal(loc=1500, scale=100, size=n_samples)  # rpm
    torque = np.random.normal(loc=40, scale=5, size=n_samples)  # Nm
    desgaste = np.clip(np.random.randint(0, 240, size=n_samples), 0, 240)  # minutos de uso

    # Falha e tipo de falha
    falhou = np.random.choice([0, 1], size=n_samples, p=[0.9, 0.1])
    tipos_falha = ["No Failure", "Power Failure", "Tool Wear Failure", "Overstrain Failure", "Random Failure"]
    tipo_falha = [np.random.choice(tipos_falha) if f == 1 else "No Failure" for f in falhou]

    # DataFrame final
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
