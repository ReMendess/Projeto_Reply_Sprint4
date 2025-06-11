# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
<a href= "https://www.fiap.com.br/"><img src="assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Admnistração Paulista" border="0" width=40% height=40%></a>
</p>

<br>

# Enterprise Challenge - Sprint 2 - Reply

## Nome do Grupo

- Arthur Luiz Rosado Alves -> RM562061
- Renan de Oliveira Mendes -> RM563145



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

