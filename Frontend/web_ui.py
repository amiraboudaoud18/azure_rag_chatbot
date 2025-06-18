import streamlit as st
import requests

st.set_page_config(page_title="Chatbot RH Contoso", layout="wide")

st.title("🤖 Assistant RH - Contoso")
model_choice = "gpt-4o-mini"
st.markdown(f"*Modèle utilisé :* **{model_choice}**")

# ✅ Initialisation des sessions de chat multiples
if "chats" not in st.session_state:
    st.session_state.chats = {}  # Dict de {chat_name: [messages]}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Chat principal"
    st.session_state.chats[st.session_state.current_chat] = []

# ✅ Sidebar : gestion des chats
st.sidebar.title("🗂️ Sessions de chat")

# Liste des chats existants
chat_names = list(st.session_state.chats.keys())
selected_index = chat_names.index(st.session_state.current_chat) if st.session_state.current_chat in chat_names else 0
selected_chat = st.sidebar.selectbox("Sélectionner un chat", chat_names, index=selected_index)

# Si l'utilisateur change de chat
if selected_chat != st.session_state.current_chat:
    st.session_state.current_chat = selected_chat

# Créer un nouveau chat
new_chat_name = st.sidebar.text_input("Nom du nouveau chat")
if st.sidebar.button("➕ Créer un nouveau chat") and new_chat_name:
    if new_chat_name not in st.session_state.chats:
        st.session_state.chats[new_chat_name] = []
        st.session_state.current_chat = new_chat_name
    else:
        st.sidebar.warning("Ce nom existe déjà.")

# Réinitialiser le chat courant
if st.sidebar.button("🧹 Réinitialiser le chat courant"):
    st.session_state.chats[st.session_state.current_chat] = []

# Supprimer le chat courant (sauf le chat principal)
if st.sidebar.button("🗑️ Supprimer ce chat"):
    if st.session_state.current_chat != "Chat principal":
        del st.session_state.chats[st.session_state.current_chat]
        st.session_state.current_chat = "Chat principal"
        st.sidebar.success("Chat supprimé.")
    else:
        st.sidebar.warning("Impossible de supprimer le chat principal.")

# 🔒 On fige la session de chat au moment du rendu pour éviter les changements pendant le submit
chat_session = st.session_state.current_chat

# ✅ Formulaire de chat
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("💬 Ton message")

    col1, col2, _ = st.columns([1, 1, 8])
    with col1:
        submit = st.form_submit_button("Envoyer")
    with col2:
        reset = st.form_submit_button("Réinitialiser")

# ✅ Envoi du message
if submit and user_input:
    response = requests.post(
        "http://localhost:5000/chat",
        json={"model": model_choice, "message": user_input}
    )

    if response.status_code == 200:
        reply = response.json()["reply"]
        st.session_state.chats[chat_session].append(("Vous", user_input))
        st.session_state.chats[chat_session].append(("Assistant RH", reply))
    else:
        st.error("Erreur API : " + response.text)

# ✅ Réinitialisation via bouton
if reset:
    st.session_state.chats[chat_session] = []

# ✅ Affichage de l’historique du chat sélectionné (figé aussi)
st.subheader(f"📜 Historique - {chat_session}")
for sender, msg in st.session_state.chats[chat_session]:
    align = "right" if sender == "Vous" else "left"
    bg = "#DCF8C6" if sender == "Vous" else "#F1F0F0"
    border_color = "#34A853" if sender == "Vous" else "#4285F4"

    st.markdown(
        f"""
        <div style='text-align:{align}; margin:10px 0;'>
            <div style='
                display:inline-block;
                background-color:{bg};
                border:1px solid {border_color};
                border-radius:10px;
                padding:10px;
                max-width:70%;
                word-wrap:break-word;
                text-align:left;
            '>
                <strong>{sender}</strong>: {msg}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
