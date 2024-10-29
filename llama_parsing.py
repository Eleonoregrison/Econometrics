import os
import pdfplumber
from groq import Groq

client = Groq(api_key=os.environ.get("econometrics_parsing"),)
def get_CIR (contenu) : 
    with open(file_path, "r", encoding="utf-8") as fichier:
        contenu = fichier.read()  
    chat_completion = client.chat.completions.create(messages=[{"role": "user", "content": "Quelle est le montant de crédit impôt recherche reçu par l'entreprise dont le bilan comptable est le suivant : {contenu}", }], model="llama3-8b-8192")
    print(chat_completion.choices[0].message.content)

