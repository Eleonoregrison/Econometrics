import os
import pdfplumber
from groq import Groq

client = Groq(api_key="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")

def get_CIR (file_path) : 
    with open(file_path, "r", encoding="utf-8") as fichier:
        contenu = fichier.read()  
    chat_completion = client.chat.completions.create(messages=[{"role": "user", "content": f"Quelle est le montant en euros de crédit impôt recherche reçu par l'entreprise dont le document suivant : {contenu}. Retourner uniquement le montant, sans explications.", }], model="llama-3.1-8b-instant")
    print(chat_completion.choices[0].message.content)

get_CIR('/Users/eleonoregrison/Documents/2A/Econometrics/Econometrics/dossier_siren/500757901_2017-12-31.txt')




