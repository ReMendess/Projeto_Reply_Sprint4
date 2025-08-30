
-- Tabela: Maquina
CREATE TABLE Maquinas (
    id_maquina INT IDENTITY(1,1) PRIMARY KEY,
    nome_maquina NVARCHAR(100) NOT NULL,
    qualidade_maquina NVARCHAR(20) NULL,
    modelo NVARCHAR(50) NULL,
    status_maquina NVARCHAR(20) NOT NULL DEFAULT 'Ativa',
  
    CONSTRAINT CK_Maquina_Status CHECK (status_maquina IN ('Ativa', 'Em Manutenção', 'Desativada'))
    CONSTRAINT CK_Maquina_Qualidade CHECK (qualidade_maquina IN ('Ruim', 'Média', 'Boa'))
);


-- Tabela: Sensor
CREATE TABLE Sensores (
    id_sensor INT IDENTITY(1,1) PRIMARY KEY,
    tipo_sensor NVARCHAR(50) NOT NULL,           -- Ex.: Temperatura, Vibração
    unidade_medida NVARCHAR(20) NOT NULL,        -- Ex.: °C, Hz, Bar
    status_sensor NVARCHAR(20) NOT NULL DEFAULT 'Ativa', 
    limite_minimo DECIMAL(10,2) NULL,
    limite_maximo DECIMAL(10,2) NULL,
    id_maquina INT NOT NULL,
  
    CONSTRAINT FK_Sensor_Maquina FOREIGN KEY (id_maquina) 
        REFERENCES Maquina(id_maquina)
        ON DELETE CASCADE,
  
    -- restrição: se informado, limite máximo >= limite mínimo
    CONSTRAINT CK_Sensor_Limites CHECK (
        limite_minimo IS NULL OR limite_maximo IS NULL OR limite_maximo >= limite_minimo
    )
    CONSTRAINT CK_Sensor_Status CHECK (status_sensor IN ('Ativo', 'Em Manutenção', 'Desativado'))
);


-- Tabela: Leitura_Sensor
CREATE TABLE Leitura_Sensor (
    id_leitura BIGINT IDENTITY(1,1) PRIMARY KEY,
    id_sensor INT NOT NULL,
    data_leitura DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    valor DECIMAL(18,4) NOT NULL,
    CONSTRAINT FK_Leitura_Sensor FOREIGN KEY (id_sensor) 
        REFERENCES Sensor(id_sensor)
        ON DELETE CASCADE,
    -- valor não pode ser absurdo: ex. maior que 1 bilhão
    CONSTRAINT CK_Leitura_Valor CHECK (valor > -1000000000 AND valor < 1000000000)
);

-- Tabela: Falha
CREATE TABLE Falha (
    id_falha INT IDENTITY(1,1) PRIMARY KEY,
    id_maquina INT NOT NULL,
    id_sensor INT NULL, 
    descricao NVARCHAR(255) NOT NULL,
    nivel_severidade NVARCHAR(20) NOT NULL,
    data_ocorrencia DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    status_falha NVARCHAR(20) NOT NULL DEFAULT 'Aberta',
  
    CONSTRAINT FK_Falha_Maquina FOREIGN KEY (id_maquina) 
        REFERENCES Maquina(id_maquina)
        ON DELETE CASCADE,
    CONSTRAINT FK_Falha_Sensor FOREIGN KEY (id_sensor) 
        REFERENCES Sensor(id_sensor)
        ON DELETE SET NULL,
  
    -- severidade deve ser uma das opções
    CONSTRAINT CK_Falha_Severidade CHECK (nivel_severidade IN ('Baixo', 'Médio', 'Alto', 'Crítico')),
  
    -- status controlado
    CONSTRAINT CK_Falha_Status CHECK (status_falha IN ('Aberta', 'Em análise', 'Resolvida'))
);
