import streamlit as st
from streamlit_folium import st_folium
import folium

st.title("Mapa / Layout da Fábrica")

# coordenadas exemplo
coords = {
    "Máquina A": (-23.560, -46.656),
    "Máquina B": (-23.5605, -46.6565),
}

m = folium.Map(location=[-23.560, -46.656], zoom_start=18)

for name, (lat, lon) in coords.items():
    popup_html = f"<b>{name}</b><br>Sensor: Temperatura, Vibração<br><button onclick=\"window.postMessage({{'machine':'{name}'}}, '*')\">Selecionar</button>"
    folium.Marker([lat, lon], popup=folium.Popup(popup_html, max_width=250)).add_to(m)

st_folium(m, width=700, height=500)

# Captura seleção via st.session_state ou via callback JS (complexo) — alternativa: clicar e selecionar na lista
selected = st.selectbox("Selecione máquina", list(coords.keys()))
st.markdown("**Descrição:** Máquina selecionada: " + selected)
