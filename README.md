# 🤖 Azure RAG Chatbot

This is an **AI-powered HR chatbot** using **Azure OpenAI + Azure Cognitive Search**, built with:

- 🔥 Flask backend (API)
- 🧼 Streamlit frontend (chat UI)
- 🔎 Azure Cognitive Search (RAG - Retrieval-Augmented Generation)

## Run the app

### Clone the repo
```bash
git clone  https://github.com/amiraboudaoud18/azure_rag_chatbot.git
cd azure_rag_chatbot

### Create virtual environments and install dependencies
#### Backend (Flask)
cd backend
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt

#### Frontend (Streamlit)
Open a new terminal window:
cd frontend
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt

### Run the application

#### Step 1: Run the Flask backend (in one terminal)
cd backend
venv\Scripts\activate
python app.py

#### Step 2: Run the Streamlit frontend (in another terminal)
cd frontend
venv\Scripts\activate
streamlit run web_ui.py


