-- Tabela: Maquinas
CREATE TABLE Maquinas (
    id_maquina NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome_maquina NVARCHAR2(100) NOT NULL,
    qualidade_maquina NVARCHAR2(20) NULL,
    modelo NVARCHAR2(50) NULL,
    status_maquina NVARCHAR2(20) DEFAULT 'Ativa' NOT NULL,
    
    CONSTRAINT CK_Maquina_Status CHECK (status_maquina IN ('Ativa', 'Em Manutenção', 'Desativada')),
    CONSTRAINT CK_Maquina_Qualidade CHECK (qualidade_maquina IN ('Ruim', 'Média', 'Boa'))
);

-- Tabela: Sensores
CREATE TABLE Sensores (
    id_sensor NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tipo_sensor NVARCHAR2(50) NOT NULL,
    unidade_medida NVARCHAR2(20) NOT NULL,
    status_sensor NVARCHAR2(20) DEFAULT 'Ativo' NOT NULL, 
    limite_minimo NUMBER(10,2) NULL,
    limite_maximo NUMBER(10,2) NULL,
    id_maquina NUMBER NOT NULL,
    
    CONSTRAINT FK_Sensor_Maquina FOREIGN KEY (id_maquina) 
        REFERENCES Maquinas(id_maquina)
        ON DELETE CASCADE,
    
    CONSTRAINT CK_Sensor_Limites CHECK (
        limite_minimo IS NULL OR limite_maximo IS NULL OR limite_maximo >= limite_minimo
    ),
    CONSTRAINT CK_Sensor_Status CHECK (status_sensor IN ('Ativo', 'Em Manutenção', 'Desativado'))
);

-- Tabela: Leitura_Sensor
CREATE TABLE Leitura_Sensor (
    id_leitura NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_sensor NUMBER NOT NULL,
    data_leitura TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
    valor NUMBER(18,4) NOT NULL,
    
    CONSTRAINT FK_Leitura_Sensor FOREIGN KEY (id_sensor) 
        REFERENCES Sensores(id_sensor)
        ON DELETE CASCADE,
    
    CONSTRAINT CK_Leitura_Valor CHECK (valor > -1000000000 AND valor < 1000000000)
);

-- Tabela: Falha
CREATE TABLE Falha (
    id_falha NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_maquina NUMBER NOT NULL,
    id_sensor NUMBER NULL, 
    descricao NVARCHAR2(255) NOT NULL,
    nivel_severidade NVARCHAR2(20) NOT NULL,
    data_ocorrencia TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
    status_falha NVARCHAR2(20) DEFAULT 'Aberta' NOT NULL,
    
    CONSTRAINT FK_Falha_Maquina FOREIGN KEY (id_maquina) 
        REFERENCES Maquinas(id_maquina)
        ON DELETE CASCADE,
    CONSTRAINT FK_Falha_Sensor FOREIGN KEY (id_sensor) 
        REFERENCES Sensores(id_sensor)
        ON DELETE SET NULL,
    
    CONSTRAINT CK_Falha_Severidade CHECK (nivel_severidade IN ('Baixo', 'Médio', 'Alto', 'Crítico')),
    CONSTRAINT CK_Falha_Status CHECK (status_falha IN ('Aberta', 'Em análise', 'Resolvida'))
);
