import pandas as pd
import numpy as np


def create_dummy_layout():
# Retorna dicionário com máquinas e coordenadas (exemplo)
return {
"Machine A": {"lat": -23.5600, "lon": -46.6560, "desc": "Linha 1 - prensa"},
"Machine B": {"lat": -23.5603, "lon": -46.6563, "desc": "Linha 2 - fresa"},
}




def aggregate_features(df: pd.DataFrame) -> pd.DataFrame:
# Exemplo simples: extrai médias e desvios
agg = {
"rpm_mean": df["rpm"].mean(),
"temp_mean": df["temperature"].mean(),
"vib_mean": df["vibration"].mean(),
"rpm_std": df["rpm"].std(),
}
return pd.DataFrame([agg])
