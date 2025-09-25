# pages/3_Predicao_Alerta.py
import streamlit as st
import joblib
import requests
from twilio.rest import Client

st.title("Predição de Risco e Alerta")

model = joblib.load("model/model.pkl")  # seu modelo treinado
df = st.session_state.get("sim_data")
phone = st.text_input("Número de celular (formato internacional, ex +5511999999999)")

if st.button("Rodar predição") and df is not None:
    # exemplo: extrair features médias
    X = df[["rpm","vibration","temperature"]].mean().values.reshape(1,-1)
    prob = model.predict_proba(X)[0,1]  # probabilidade de falha
    st.metric("Probabilidade de falha", f"{prob:.2%}")
    threshold = st.slider("Limiar para alerta", 0.1, 0.9, 0.6)
    if prob >= threshold:
        st.warning("Risco alto! Enviando alerta WhatsApp...")
        # Exemplo Twilio
        TW_SID = st.secrets["TW_SID"]
        TW_AUTH = st.secrets["TW_AUTH"]
        TW_WHATSAPP_FROM = "whatsapp:+14155238886"  # exemplo sandbox Twilio
        client = Client(TW_SID, TW_AUTH)
        try:
            msg = client.messages.create(
                body=f"Alerta: risco de falha {prob:.1%} na máquina X. Ação necessária.",
                from_=TW_WHATSAPP_FROM,
                to=f"whatsapp:{phone}"
            )
            st.success("Alerta enviado via Twilio.")
        except Exception as e:
            st.error("Erro ao enviar alerta: " + str(e))
