import oracledb
import pandas as pd


# Conexão
conn = oracledb.connect(user="RM563145", password="260399", dsn="oracle.fiap.com.br:1521/ORCL")

# Query para buscar o último registro
query = """
SELECT id_leitura, data_leitura, valor, s.tipo_sensor, m.nome_maquina
FROM leitura_sensor l
JOIN sensores s ON l.id_sensor = s.id_sensor
JOIN maquinas m ON s.id_maquina = m.id_maquina
WHERE l.data_leitura = (
    SELECT MAX(data_leitura) FROM leitura_sensor
)
"""

# Ler no Pandas
df = pd.read_sql(query, conn)

# Exibir no Streamlit
print(df)
