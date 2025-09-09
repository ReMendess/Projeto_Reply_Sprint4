# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
<a href= "https://www.fiap.com.br/"><img src="assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Admnistração Paulista" border="0" width=40% height=40%></a>
</p>

<br>

# Enterprise Challenge - Sprint 3 - Reply

## Nome do Grupo

- Arthur Luiz Rosado Alves -> RM562061
- Renan de Oliveira Mendes -> RM563145


### Link do vídeo: https://youtu.be/FiJrwkl0I2Q

## Sumário

[1. Solução e Planejamento](#c1)

[2. Banco de Dados - Diagrama Entidade-Relacionamento (DER)](#c2)

[3. Machine Learning](#c3)

[4. Diagrama](#c4)

<br>

# <a name="c1"></a>1. Solução e Planejamento

Continuando com o desenvolvimento de nossa solução que consiste em uma plataforma inteligente de monitoramento industrial. Ela é baseada na integração de tecnologias como sensores IoT, armazenamento em nuvem, inteligência artificial e visualização de dados, com o objetivo é detectar antecipadamente possíveis falhas em equipamentos.
Veja toda nossa proposta previamente explicada em: https://github.com/ReMendess/Enterprise_ChallengeSprint_1_Reply

# <a name="c2"></a>2. Banco de Dados - Diagrama Entidade-Relacionamento (DER)

Nessa terceira etapa, criamos um Diagrama Entidade-Relacionamento (DER).

Arquivo: scriptSQL.sql

Primeiro realizamos uma modelagem em uma ferramenta básica, com a intenção de identificar as principais entidades. Para definir as entidades, consideramos quais dados precisamos monitorar e guardar para treinar nosso modelo de Machine Learning de predição de falhas mecânicas. 
Chegamos a quatro principais entidades: Máquinas, Sensores, Leitura do Sensor e Falha.
Na entidade Máquina armazenaremos o nome, modelo, qualidade atual e status. Qualidade se refere a condição da máquina, que pode variar entre: Ruim, média ou boa. Status se refere se a máquina está ativa, em manutenção o desativada.

Na entidade Sensores armazenaremos o tipo de sensor, a unidade medida pelo sensor, e dois valores de limites máximos e minímo, para ajudar a determinar e identificar anomalias. Além de status.

Na entidade Leitura do Sensor deve ser armazenado o valor captado, data e hora de captação.

Na entidade Falha será guardado a descrição da falha captada, nível de severidade, data registrada da ocorrência e status da falha, deve variar entre em aberto, em análise ou resolvido.

Com essas entidades e atributos podemos maximizar a captura de dados relevantes e uteis para identificar as falhas, suas causas e correlações. E também monitorar e classificar a qualidade dos equipamentos. Permitindo uma análise mais profunda e até mesmo a implementação de modelos de inteligência artificial para contribuir com a predição de manutenção.

### Diagrama Entidade-Relacionamento inicial
<p align="center">
<img src="/assets/Reply3.png" alt="Sensores"></a>
</p>


## Entidades

### **Maquinas**
**Atributos:**
- `id_maquina` (PK) → Identificador único  
- `nome_maquina` → Nome ou código interno
- `qualidade_maquina` → (Ruim, Média, Boa) 
- `modelo` → Modelo da máquina   
- `status_maquina` → (Ativa, Em manutenção, Desativada)  

---

### **Sensores**
**Atributos:**
- `id_sensor` (PK)  
- `tipo_sensor` → (Temperatura, Vibração, Pressão, Corrente elétrica etc.)
- `unidade_medida` → (°C, Hz, Bar, A)  
- `status_sensor` → (Ativo, Em manutenção, Desativado)
- `limite_minimo` → Valor considerado normal mínimo  
- `limite_maximo` → Valor considerado normal máximo  
- `id_maquina` (FK) → Relaciona o sensor à máquina  

---

### **Leitura_Sensor**
(para armazenar os dados coletados continuamente)  

**Atributos:**
- `id_leitura` (PK)  
- `data_leitura` → Data e hora da leitura  
- `valor` → Medição captada pelo sensor
- `id_sensor` (FK)  

---

### **Falha**
(registra os problemas ou alertas detectados em uma máquina)  

**Atributos:**
- `id_falha` (PK)
- `descricao` → Descrição da falha 
- `nivel_severidade` → (Baixo, Médio, Alto, Crítico)  
- `data_ocorrencia`  
- `status_falha` → (Aberta, Em análise, Resolvida)
- `id_maquina` (FK)  
- `id_sensor` (FK) 

---

## 2. Relações e Cardinalidades

- **Máquina (1) — (N) Sensor**  
  Uma máquina pode ter vários sensores, mas cada sensor pertence a uma única máquina.  

- **Sensor (1) — (N) Leitura_Sensor**  
  Um sensor gera muitas leituras ao longo do tempo, mas cada leitura pertence a apenas um sensor.  

- **Máquina (1) — (N) Falha**  
  Uma máquina pode apresentar várias falhas, mas cada falha pertence a uma máquina específica.  

- **Sensor (0..1) — (N) Falha**  
  Uma falha pode estar associada a um sensor (ex: superaquecimento detectado por sensor de temperatura),  
  mas também pode estar ligada à máquina em geral (ex: falha elétrica).  

### Diagrama Entidade-Relacionamento Final
Criado dentro do Oracle Database.
<p align="center">
<img src="/assets/DER_Reply3.png"></a>
</p>

Com essa estrutura já podemos armazenar os dados e futuramente utilizar ferramentas como Streamlit ou semelhantes para gerar uma visualização profunda e datalhada dos dados.

# <a name="c3"></a>3. Machine Learning

Utilizando o dataset "predictive_maintenance.csv" obtemos 10 mil registros de medições de sensores em máquinas industriais. Utilizamos esse dataset para treinar os modelos de machine learning, com o objetivo de criar modelos de predição de risco de falha de máquinas industriais.

Link do dataset: https://www.kaggle.com/datasets/shivamb/machine-predictive-maintenance-classification
Arquivo Notebook Python: Reply (4).ipynb

### Features
ID Único → Identificador numérico único de cada registro no dataset.

ID Produto → Código ou identificador da máquina.

Tipo → Categoria ou classe da máquina ou do processo em execução.

Temperatura do ar [K] → Medição da temperatura ambiente ao redor da máquina, registrada em Kelvin.

Temperatura do processo [K] → Medição da temperatura interna do processo produtivo, em Kelvin.

Velocidade de rotação [rpm] → Rotação do eixo da máquina em rotações por minuto (rpm).

Torque [Nm] → Força de torção aplicada pelo eixo da máquina, medida em Newton-metro (Nm).

Desgaste ferramenta [min] → Tempo acumulado de uso da ferramenta de corte, indicado em minutos.

Falhou → Indicador binário (sim/não) que informa se ocorreu falha na máquina/processo.

Tipo de falha → Descrição da falha ocorrida.

<p align="center">
<img src="/assets/ML.png"></a>
</p>

## Tratamento dos dados

- Inicialmente, foi necessário fazer um tratamento nas colunas do data-set, que estavam em ingles.

<p align="center">
<img src="/assets/ML2.png"></a>
</p>

- Verificamos se haviam dados nulos, e quais os tipos de dados presentes no DataSet.

<p align="center">
<img src="/assets/ML3.png"></a>
</p>

- Aplicamos o tratamento de Features, Removendo algumas colunas que seriam "inúteis" para o treinamento do modelo como "Id Produto", "Id Único".

- Detectamos alguns dados categóricos e passamos todos para a escala númerica.

## Treinamento e Seleção dos Modelos

- Diante do problema proposto "Predição de Manutenção", utilizamos um algoritmo de Classificação pois se trata de dados rótulados.

- Verificamos alguns outliers, e removemos os mesmos.

<p align="center">
<img src="/assets/ML4.png"></a>
</p>


- Dividimos os dados em 70% treino e 30% teste, para aplicar os modelos de Classificação.

<p align="center">
<img src="/assets/ML5.png"></a>
</p>

### Random Forest Classifier

No Geral o Modelo de Random Forest apresentou um baixo desempenho com o dataset, no qual apresenta resultados "enganosos" pois mesmo com a precisão bastante alta do modelo, apresenta dificuldade de intepretar falhas nas máquinas.

Recall: **52% sinaliza que o modelo está tendo dificuldade em detectar as máquinas que apresentam falhas.

F1-Score: 63% Uma métrica que combina a precisão do modelo, juntamente com o Recall. Nesse caso a precisão não indica tanta importancia, pois queremos detectar o caso em que as máquinas falham, que no caso são apenas 3.4 % das vezes.

<p align="center">
<img src="/assets/ML6.png"></a>
</p>

### Gradient Boost

 O modelo **Gradient Boost se mostrou muito mais eficiente, mesmo diante do desbalanceamento do data set, no qual apenas **3.4% dos dados correspondiam a falhas de maquinas, o que dificultou o treinamento dos outros modelos. O **Gradient Boost se mostrou muito eficiente nessa situação uma vez em que se trata de uma técnica de otimização interativa em que o modelo aprende com seus próprios erros. Apresentando então um Bom desempenho com o data set escolhido.

 Recall: **77%, essa métrica simboliza que de 100 falhas de máquina o modelo detecta 83. Assim sendo muito eficiente em um cenário real de produção, o que acarretaria a menos paradas na fábrica.

F1-Score :** 67 %, simboliza os possiveis "alarmes falsos" de paradas, assim equilibra a precisão do modelo, juntamente com a predicão de falhas.

<p align="center">
<img src="/assets/ML7.png"></a>
</p>

# <a name="c4"></a>4. Diagrama
Abaixo nossa solução proposta

<p align="center">
<img src="diagrama.drawio" alt="Driagrama da solução"></a>
</p>

