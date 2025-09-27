dados = {
    'UDI': [1, 2, 3, 4, 5],
    'Product ID': ['M14860', 'L47181', 'L47182', 'L47183', 'L47184'],
    'Type': ['M', 'L', 'L', 'L', 'L'],
    'Air temperature [K]': [298.1, 298.2, 298.1, 298.2, 298.2],
    'Process temperature [K]': [308.6, 308.7, 308.5, 308.6, 308.7],
    'Rotational speed [rpm]': [1551, 1408, 1498, 1433, 1408],
    'Torque [Nm]': [42.8, 46.3, 49.4, 39.5, 40.0],
    'Tool wear [min]': [0, 3, 5, 7, 9],
    'Target': [0, 0, 0, 0, 0],
    'Failure Type': ['No Failure']*5
}

df = pd.DataFrame(dados)

# ==========================
# Renomear colunas
# ==========================
colunas = [
    'ID Unico',
    'ID Produto',
    'Tipo',
    'Temperatura do ar [K]',
    'Temperatura do processo [K]',
    'Velocidade de rotação [rpm]',
    'Torque [Nm]',
    'Desgaste ferramenta [min]',
    'Falhou',
    'Tipo de falha'
]
df.columns = colunas

# ==========================
# Definir transformação
# ==========================
# Encoder para a coluna "Tipo"
ordinal_encoder = OrdinalEncoder(categories=[['L', 'M', 'H']])

# Criar transformer que aplica apenas no "Tipo"
col_transformer = ColumnTransformer(
    transformers=[
        ("tipo_encoder", ordinal_encoder, ["Tipo"])
    ],
    remainder="passthrough"
)

# Pipeline final
pipeline = Pipeline(steps=[
    ("encode", col_transformer)
])

# ==========================
# Executar pipeline
# ==========================
dados_transformados = pipeline.fit_transform(df)
