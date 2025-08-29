# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
<a href= "https://www.fiap.com.br/"><img src="assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Admnistração Paulista" border="0" width=40% height=40%></a>
</p>

<br>

# Enterprise Challenge - Sprint 3 - Reply

## Nome do Grupo

- Arthur Luiz Rosado Alves -> RM562061
- Renan de Oliveira Mendes -> RM563145


# O que fazer:
Na parte do Banco de Dados:

Elaborar um Diagrama Entidade-Relacionamento (DER) completo;

Definir as principais tabelas, campos, chaves primárias e relacionamentos;

Prever restrições de integridade (exemplo: tipos de dados, limites de tamanho etc.);

Criar um script SQL inicial de criação das tabelas (CREATE TABLE);

Na parte da ML Básico:

Escolher uma tarefa simples de ML: classificação, regressão ou análise preditiva simples;

Utilizar Scikit-learn, Pandas, NumPy ou outras ferramentas vistas no material do curso;

Treinar um modelo básico, utilizando o conjunto de dados da entrega anterior. Aqui, a sugestão é que tenha pelo menos 500 leituras de cada sensor. Caso não tenha, você pode trabalhar com a ingestão de dados artificiais no seu banco e justificar na documentação;

Gerar uma visualização simples do resultado (pode ser um gráfico de barras, linha, matriz de confusão ou até um scatter plot). Justificar qual gráfico adotado;

Documentar o código, os dados usados e as análises obtidas, trazer prints dos gráficos e justificar os resultados. 

4)   REQUISITOS TÉCNICOS E FUNCIONAIS

Banco de Dados:

Diagrama ER (Entidade-Relacionamento) com entidades, atributos, relacionamentos, cardinalidades e chaves primárias/estrangeiras;

Descrição de cada entidade e campo, explicando o motivo de sua inclusão;

Script SQL inicial com o código de criação das tabelas;

Prints ou exportações gráficas do modelo criado na ferramenta utilizada;

Previsão de integração futura com ferramentas de visualização de dados. 

ML Básico:

Código Python (Jupyter ou .py) mostrando o processo de treino do modelo;

Explicação de qual foi o problema escolhido (exemplo: classificação de níveis de temperatura, previsão de um valor futuro etc.);

Dataset utilizado (pode ser CSV com os dados simulados da fase anterior);

Print ou gráfico dos resultados do modelo (exemplo: accuracy, gráfico de predição, matriz de confusão).


5)   ENTREGÁVEIS

5.1) Documentação via GitHub Público

A entrega deverá ser feita por meio de um repositório público no GitHub, contendo:

Arquivos do projeto de modelagem de banco de dados (.dmd, .sql ou outro formato);

Imagem do Diagrama ER exportado;

Script SQL de criação das tabelas;

Código-fonte do modelo de Machine Learning (Python ou Jupyter Notebook);

CSV ou fonte de dados utilizados para treino/teste;

Gráficos e/ou prints dos resultados obtidos com o modelo;

README explicativo, descrevendo:

Como o banco de dados foi modelado;

Como foi feita a implementação do ML;

Principais resultados obtidos.

Vídeo de até 5 minutos explicando e justificando, com áudio (sem música de fundo), todo o seu projeto dessa fase. Postar no YouTube como “não listado” e adicionar o link no README.


## Sumário

[1. Solução e Planejamento](#c1)

[2. Sensores - Wokwi](#c2)

[3. Análise Exploratória](#c3)

[4. Diagrama](#c4)

<br>

# <a name="c1"></a>1. Solução e Planejamento

Continuando com o desenvolvimento de nossa solução que consiste em uma plataforma inteligente de monitoramento industrial. Ela é baseada na integração de tecnologias como sensores IoT, armazenamento em nuvem, inteligência artificial e visualização de dados, com o objetivo é detectar antecipadamente possíveis falhas em equipamentos.
Veja toda nossa proposta previamente explicada em: https://github.com/ReMendess/Enterprise_ChallengeSprint_1_Reply

# <a name="c2"></a>2. Sensores - Wokwi

Nessa segunda etapa, criamos um circuito virtual com ESP32. Simulamos e habilitamos os sensores, utilizando o Wokwi. Habilitamos o funcionamento com um código em c (codigo_wokwi_leitura.c).

ESP32 - placa de centro de controle.
DHT22 - sensor de temperatura e umidade.
MPU6050 - sensor acelerômetro e giroscópio.
Potenciômetro - simulando sensor de corrente.

Sensor	Pino / Interface	Mede o quê	Tipo
DHT22	Pino 26 (digital)	Temperatura e umidade	Sensor digital ambiental
MPU6050	I2C (SDA 22, SCL 23)	Aceleração (vibração) e rotação	Acelerômetro / giroscópio
Potenciômetro	Pino 33 (analógico)	Corrente simulada (0 a 30 A)	Simulad


  | Sensor        | Pino / Interface |      Medição               |
  |-----------    |------------------|----------------------      |
  |DHT22          |Pino 26           | Temperatura e umidade      | 
  |MPU6050        |PI2C              | Vibração e rotação         |
  |Potenciômetro  |Pino 33           |Corrente simulada 0 a 30 A  |


<p align="center">
<img src="/Sprint_2/simulacao_circuito.png" alt="Sensores"></a>
</p>


Utilizamos um Monitor Serial para acompanhar em tempo real as medições

<p align="center">
<img src="/Sprint_2/monitor_serial.png" alt="Sensores"></a>
</p>



# <a name="c3"></a>3. Análise Exploratória

Simulamos os dados captados para realizar uma análise exploratória. E juntamento com Streamlit, criamos uma interface que possibilita separar o número de amostrar, realizar uma análise estastístia e cria três gráficos: Dispesão, Histograma e um Boxplot.
Acesse a aplicação pelo link: https://projetoreply-gc6q63kp35czpwwwfc2std.streamlit.app/
Arquivo de código (dados_e_analise.py).

<p align="center">
<img src="/assets/streamlit.png" alt="Sensores"></a>
</p>

<p align="center">
<img src="/assets/streamlit2.png" alt="Sensores"></a>
</p>

<p align="center">
<img src="/assets/streamlit3.png" alt="Sensores"></a>
</p>


<p align="center">
<img src="/assets/streamlit4.png" alt="Sensores"></a>
</p>



# <a name="c4"></a>4. Diagrama
Abaixo nossa solução proposta

<p align="center">
<img src="diagrama.drawio" alt="Driagrama da solução"></a>
</p>

