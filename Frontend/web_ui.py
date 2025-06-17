import streamlit as st
import requests

st.set_page_config(page_title="Chatbot RH Contoso", layout="wide")

st.title("🤖 Assistant RH - Contoso")

model_choice = st.selectbox("Choisis un modèle :", ["gpt-4o-mini"]) # Match with backend

user_input = st.text_input("💬 Ton message")

if "history" not in st.session_state:
    st.session_state.history = []

if st.button("Envoyer") and user_input:
    response = requests.post(
        "http://localhost:5000/chat",
        json={"model": model_choice, "message": user_input}
    )

    if response.status_code == 200:
        reply = response.json()["reply"]
        st.session_state.history.append(("Vous", user_input))
        st.session_state.history.append(("Bot", reply))
    else:
        st.error("Erreur API : " + response.text)

st.subheader("📜 Historique de la conversation")
for sender, msg in st.session_state.history:
    if sender == "Vous":
        st.markdown(f"**{sender}**: {msg}")
    else:
        st.markdown(f"💬 **{sender}**: {msg}")
