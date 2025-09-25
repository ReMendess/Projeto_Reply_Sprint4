import streamlit as st
from streamlit_image_coordinates import streamlit_image_coordinates

st.title(" Fábrica Interativa - ")

# Inicializa lista de máquinas
if "maquinas" not in st.session_state:
    st.session_state.maquinas = []

# Tipos de máquinas disponíveis
tipos_maquina = ["Máquina de Corte", "Prensa", "Esteira", "Empilhadeira", "Armazém"]
qualidade_maquinas = ["Baixa", "Media", "Alta"]
mapa_qualidade = {"Baixa": "L", "Media": "M", "Alta": "H"}

# Exibe a planta redimensionada e captura clique
coords = streamlit_image_coordinates("industria.png", width=500)

# Se clicou, abre formulário para cadastrar máquina
if coords is not None:
    with st.form("cadastro_maquina", clear_on_submit=True):
        tipo = st.selectbox("Tipo de Máquina", tipos_maquina)
        qualidade = st.selectbox("Qualidade de Maquina", qualidade_maquinas)
        Id_Maquina = st.text_input("Código ou identificador da máquina.")

        temperaturaAr = st.slider("Temperatura do Ar [K]", 250, 400, (290, 350))
        temperaturaProcesso = st.slider("Temperatura do processo [K]", 250, 400, (290, 350))

        velocidadeRotacao = st.number_input("Velocidade de rotação [rpm]", value=1300, min_value=500, max_value=10000)
        torque = st.number_input("Torque [Nm]", value=50, min_value=10, max_value=500)
        desgasteMaq = st.number_input("Desgaste ferramenta [min]", value=3, min_value=1, max_value=60)

        submit = st.form_submit_button("Adicionar Máquina")

        if submit:
            st.session_state.maquinas.append({
                "Identificador": Id_Maquina,
                "tipo": tipo,
                "Qualidade": mapa_qualidade[qualidade],  # já mapeia para L/M/H
                "x": coords["x"],
                "y": coords["y"],
                "temperaturaAr": sum(temperaturaAr) / 2,  # salva média
                "temperaturaProcesso": sum(temperaturaProcesso) / 2,
                "rotacao": velocidadeRotacao,
                "torque": torque,
                "desgaste": desgasteMaq,
            })
            st.success(f" {tipo} ({Id_Maquina}) adicionada!")

# Lista de máquinas já criadas
st.subheader(" Máquinas Registradas")

if not st.session_state.maquinas:
    st.info("Nenhuma máquina cadastrada ainda. Clique na planta para adicionar.")
else:
    for m in st.session_state.maquinas:
        titulo = f"{m['tipo']} - ({m['Identificador']})"
        with st.expander(titulo):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Posição:** x={m['x']}, y={m['y']}")
                st.markdown(f"**Temp. Ar:** {m['temperaturaAr']:.1f} K")
                st.markdown(f"**Temp. Processo:** {m['temperaturaProcesso']:.1f} K")
            with col2:
                st.markdown(f"**Rotação:** {m['rotacao']} rpm")
                st.markdown(f"**Torque:** {m['torque']} Nm")
                st.markdown(f"**Desgaste:** {m['desgaste']} min")
                st.markdown(f"**Qualidade:** {m['Qualidade']}")
