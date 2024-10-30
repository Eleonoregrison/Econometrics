mport os
import pdfplumber
from groq import Groq

# La première partie est un test avec l'API Groq mais il y des problèmes de token

client = Groq(api_key="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")

def get_CIR (file_path) : 
    with open(file_path, "r", encoding="utf-8") as fichier:
        contenu = fichier.read()  
    chat_completion = client.chat.completions.create(messages=[{"role": "user", "content": f"Quel est le montant en euros de crédit impôt recherche (CIR) reçu par l'entreprise dans le document suivant : {contenu}. Retourner uniquement le nombre correspondant à la valeur du CIR, sans explications. ", }], model="llama-3.1-8b-instant")
    print(chat_completion.choices[0].message.content)

get_CIR('/Users/eleonoregrison/Documents/2A/Econometrics/Econometrics/dossier_siren/500363254_2016-12-31.txt')




# Utili

import os
from google.cloud import aiplatform

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"apt-honor-440210-n8-5c947fe1a7ad.json"

# +
import base64
import vertexai
from vertexai.generative_models import GenerativeModel, Part, SafetySetting

def open_file (file_path) : 
    with open(file_path, "r", encoding="utf-8") as fichier:
        contenu = fichier.read()
    return contenu

def generate(file_path):
    contenu = open_file(file_path)
    vertexai.init(project="apt-honor-440210-n8", location="us-central1")
    model = GenerativeModel(
        "gemini-1.5-flash-002",
    )
    responses = model.generate_content(
        [f"""Quel est le montant en euros de crédit impôt recherche (CIR) reçu par l\'entreprise dans le document suivant {contenu}? Retourner uniquement le montant sans explications et sans unités 
    """
],
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=True,
    )

    for response in responses:
        print(response.text, end="")


generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
}

safety_settings = [
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
]

generate('/Users/eleonoregrison/Documents/2A/Econometrics/Econometrics/dossier_siren/500363254_2016-12-31.txt')
# -
