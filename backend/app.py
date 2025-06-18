
from flask import Flask, request, jsonify
from openai import AzureOpenAI
import config
import os
import re
import pandas as pd

app = Flask(__name__)

# Load the employee dataset
df = pd.read_csv("hr_dataset_fr_new.csv", encoding="latin1", delimiter=";")

# Azure OpenAI client
client = AzureOpenAI(
    azure_endpoint=config.AZURE_API_BASE,
    api_key=config.AZURE_API_KEY,
    api_version=config.AZURE_API_VERSION
)

def extract_target_emails(message):
    # Extract emails from the message
    return re.findall(r"[\w\.-]+@[\w\.-]+", message)

def extract_target_names(message):
    # Extract capitalized words (first names or last names)
    return re.findall(r"\b([A-ZÉÈÊÎÔÂ][a-zéèêîôâçëïü\-']+)\b", message)

def find_emails_by_name(name):
    # Search for the name (first or last) in the 'nom' column
    name = name.lower()
    matches = df[df['nom'].str.lower().str.contains(name)]
    return matches['email'].tolist()

def is_authorized(user, target_email):
    # Self-access always allowed
    if target_email.lower() == user['email'].lower():
        return True

    target_row = df[df['email'].str.lower() == target_email.lower()]
    if target_row.empty:
        return False

    target = target_row.iloc[0]

    # PDG: can see all info
    if user.get("poste", "").strip().lower() == "pdg":
        return True

    # RH: can see all info
    if user["departement"].strip().lower() == "rh":
        return True

    # Managers: can see employees in their department (but not other managers)
    if user.get("Manager", "").strip().lower() == "oui":
        if user["departement"].strip().lower() == target["departement"].strip().lower():
            if target["Manager"].strip().lower() != "oui":
                return True

    # All others: cannot see others
    return False

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")
    user_info = data.get("user", {})
    model = data.get("model", config.AZURE_DEPLOYMENT_NAME)

    # 1. Try to extract emails from the message
    targets = extract_target_emails(user_message)
    # 2. If no email found, try to extract names
    if not targets:
        names = extract_target_names(user_message)
        for name in names:
            emails = find_emails_by_name(name)
            targets.extend(emails)
    # 3. If still nothing, fallback to self
    if not targets:
        targets = [user_info["email"]]

    target_data = None
    for email in targets:
        if not is_authorized(user_info, email):
            return jsonify({"reply": f"Accès refusé. Vous n’êtes pas autorisé(e) à consulter des informations concernant {email}."})
        target_row = df[df['email'].str.lower() == email.lower()]
        if not target_row.empty:
            target_data = target_row.iloc[0].to_dict()
            break  # Take the first match

    # --- Only document names in references ---
    document_references = [
        "Base de données RH interne"
    ]

    if target_data:
        infos = "\n".join([f"{k}: {v}" for k, v in target_data.items()])
        docs = ", ".join(document_references)
        system_content = f"""Tu es un assistant RH pour l’entreprise Contoso SAS.
Voici les informations RH de la personne concernée :
{infos}
Quand tu donnes une information, indique uniquement le nom du document utilisé comme référence, par exemple : [Base de données RH interne].
À la fin de ta réponse, ajoute une section "Références utilisées" listant uniquement le ou les noms de documents utilisés pour répondre (pas les champs du tableau).
"""
    else:
        docs = ", ".join(document_references)
        system_content = f"""Tu es un assistant RH pour l’entreprise Contoso SAS.
Tu aides {user_info['nom']} ({user_info['poste']} - {user_info['departement']}). 
Tu dois répondre uniquement selon les documents internes et les autorisations du collaborateur.
Quand tu donnes une information, indique uniquement le nom du document utilisé comme référence, par exemple : [Base de données RH interne].
À la fin de ta réponse, ajoute une section "Références utilisées" listant uniquement le ou les noms de documents utilisés pour répondre (pas les champs du tableau).
"""

    prompt = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_message}
    ]

    completion = client.chat.completions.create(
        model=model,
        messages=prompt,  # contient user_info + RH data ou fallback
        temperature=0.7,
        top_p=0.9,
        max_tokens=2048,
        extra_body={
            "data_sources": [
                {
                    "type": "azure_search",
                    "parameters": {
                        "endpoint": config.AZURE_SEARCH_ENDPOINT,
                        "index_name": config.AZURE_SEARCH_INDEX,
                        "semantic_configuration": config.AZURE_SEARCH_SEMANTIC,
                        "query_type": "vector_semantic_hybrid",
                        "top_n_documents": 5,
                        "authentication": {
                            "type": "api_key",
                            "key": config.AZURE_SEARCH_KEY
                        },
                        "embedding_dependency": {
                            "type": "deployment_name",
                            "deployment_name": "text-embedding-ada-002"  # ✅ nom exact du déploiement embeddings
                        }
                    }
                }
            ]
        }
    )


    return jsonify({"reply": completion.choices[0].message.content.strip()})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
