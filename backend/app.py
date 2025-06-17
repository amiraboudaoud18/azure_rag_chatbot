from flask import Flask, request, jsonify
from openai import AzureOpenAI
import config
import os

app = Flask(__name__)

client = AzureOpenAI(
    azure_endpoint=config.AZURE_API_BASE,
    api_key=config.AZURE_API_KEY,
    api_version=config.AZURE_API_VERSION
)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")
    model = data.get("model", config.AZURE_DEPLOYMENT_NAME)

    chat_prompt = [
        {"role": "system", "content": "Tu es un assistant RH intelligent pour l’entreprise Contoso SAS."},
        {"role": "user", "content": user_message}
    ]

    completion = client.chat.completions.create(
        model=model,
        messages=chat_prompt,
        temperature=0.2,
        max_tokens=1024,
        extra_body={
        "data_sources": [
            {
                "type": "azure_search",
                "parameters": {
                    "endpoint": os.getenv("AZURE_SEARCH_ENDPOINT"),
                    "index_name": os.getenv("AZURE_SEARCH_INDEX"),
                    "semantic_configuration": os.getenv("AZURE_SEARCH_SEMANTIC"),
                    "query_type": "vector_semantic_hybrid",
                    "top_n_documents": 5,
                    "authentication": {
                        "type": "api_key",
                        "key": os.getenv("AZURE_SEARCH_KEY")
                    },
                    "embedding_dependency": {
                        "type": "deployment_name",
                        "deployment_name": "text-embedding-ada-002"
                    }
                }
            }
        ]
    }

    )

    return jsonify({"reply": completion.choices[0].message.content})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
