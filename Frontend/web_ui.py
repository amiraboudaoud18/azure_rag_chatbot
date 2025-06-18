import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Assistant RH Contoso", layout="wide")

st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        div.block-container{padding-top:1rem;}
        .stButton>button {
            background-color: #20787c !important;
            color: white !important;
            border-radius: 8px !important;
            border: none !important;
            font-weight: bold;
        }
        .stButton>button:hover {
            background-color: #15595b !important;
            color: #fff !important;
        }
    </style>
    """, unsafe_allow_html=True)

st.image("logo_transp.png", width=180)

model_choice = "gpt-4o-mini"

df = pd.read_csv("hr_dataset_fr_new.csv", encoding="latin1", delimiter=";")

# --- LOGIN POPUP ---
if "user" not in st.session_state:
    st.session_state.show_login = True

if st.session_state.get("show_login", True):
    st.markdown("### Connexion requise")
    with st.form("login_form", clear_on_submit=True):
        email_input = st.text_input("Entrez votre adresse email")
        login_submit = st.form_submit_button("Se connecter")
    if login_submit:
        user_row = df[df["email"].str.lower() == email_input.lower()]
        if not user_row.empty:
            st.session_state.user = user_row.iloc[0].to_dict()
            st.session_state.show_login = False
            st.success(f"Bienvenue {st.session_state.user['nom']}!")
            st.rerun()
        else:
            st.error("Email non reconnu.")
    st.stop()

user = st.session_state.user

if "chats" not in st.session_state or "current_chat" not in st.session_state:
    st.session_state.chats = {"Chat principal": []}
    st.session_state.current_chat = "Chat principal"


# --- GREETING ---
st.markdown(
    f"""
    <div style='background-color:#3e8b8f; color:white; padding:16px; border-radius:8px; margin-bottom:20px; font-size:18px;'>
        👋 Bonjour <b>{user['nom']}</b> ! Vous êtes connecté(e) avec l'adresse : {user['email']}
    </div>
    """,
    unsafe_allow_html=True
)

# Sidebar: chat sessions
st.sidebar.title("Sessions de chat")
chat_names = list(st.session_state.chats.keys())
selected_index = chat_names.index(st.session_state.current_chat) if st.session_state.current_chat in chat_names else 0
selected_chat = st.sidebar.selectbox("Sélectionner un chat", chat_names, index=selected_index)

if selected_chat != st.session_state.current_chat:
    st.session_state.current_chat = selected_chat

new_chat_name = st.sidebar.text_input("Nom du nouveau chat")
if st.sidebar.button("Créer un nouveau chat") and new_chat_name:
    if new_chat_name not in st.session_state.chats:
        st.session_state.chats[new_chat_name] = []
        st.session_state.current_chat = new_chat_name
    else:
        st.sidebar.warning("Ce nom existe déjà.")

if st.sidebar.button("Réinitialiser le chat courant"):
    st.session_state.chats[st.session_state.current_chat] = []

if st.sidebar.button("Supprimer ce chat"):
    if st.session_state.current_chat != "Chat principal":
        del st.session_state.chats[st.session_state.current_chat]
        st.session_state.current_chat = "Chat principal"
        st.sidebar.success("Chat supprimé.")
    else:
        st.sidebar.warning("Impossible de supprimer le chat principal.")

if st.sidebar.button("Se déconnecter"):
    for key in ["user", "show_login", "chats", "current_chat"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

chat_session = st.session_state.current_chat

# --- CHAT FORM ---
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("Ton message")
    col1, col2, _ = st.columns([1, 1, 5])
    with col1:
        submit = st.form_submit_button("Envoyer")
    with col2:
        reset = st.form_submit_button("Réinitialiser")

if submit and user_input:
    response = requests.post(
        "http://localhost:5000/chat",
        json={
            "model": model_choice,
            "message": user_input,
            "user": {
                "nom": user["nom"],
                "email": user["email"],
                "poste": user["poste"],
                "departement": user["departement"],
                "Manager": user["Manager"]
            }
        }
    )
    if response.status_code == 200:
        reply = response.json()["reply"]
        st.session_state.chats[chat_session].append(("Vous", user_input))
        st.session_state.chats[chat_session].append(("Assistant RH", reply))
    else:
        st.error("Erreur API : " + response.text)

if reset:
    st.session_state.chats[chat_session] = []

# --- CHAT HISTORY ---
st.subheader(f"Historique - {chat_session}")
for sender, msg in st.session_state.chats[chat_session]:
    align = "right" if sender == "Vous" else "left"
    bg = "#b3e5df" if sender == "Vous" else "#F1F0F0"
    border_color = "#b3e5df" if sender == "Vous" else "#b3e5df"
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
