# Utilisation de Gemini avec Google cloud (API Vertex AI)

import os
from google.cloud import aiplatform

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"apt-honor-440210-n8-5c947fe1a7ad.json" # Remplacer par votre clé 

# +
import base64
import vertexai
from vertexai.generative_models import GenerativeModel, Part, SafetySetting

def open_file (file_path) : 
    with open(file_path, "r", encoding="utf-8") as fichier:
        contenu = fichier.read()
    return contenu

def generate(file_path):
    CIR =""
    contenu = open_file(file_path)
    vertexai.init(project="apt-honor-440210-n8", location="us-central1")
    model = GenerativeModel(
        "gemini-1.5-flash-002",
    )
    responses = model.generate_content(
        [f"""Quel est le montant en euros de Crédit Impôt Recherche (CIR) reçu par l\'entreprise dans le document suivant {contenu}? Faire attention car le montant peut être écrit en milliers d'euros (k€) il faudra alors faire la conversion en euros. Si le montant est négatif, il faudra alors prendre sa valeur opposée positive. Faire attention à ne pas retourner le montant du Crédit d'Impôt pour la Compétitivité de l'Emploi (CICE) qui ne nous intéresse pas. Retourner uniquement le montant sans explications et sans unités. Si l'entreprise reçoit du CIR mais ne précise pas combien, renvoyer 'oui'. Si aucun CIR n'est perçu ou qu'aucune information concernat le CIR n'est mentionnée, renvoyer 0. 
    """
],
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=True,
    )

    for response in responses:
        CIR += response.text 
        CIR = CIR.replace('\n', '')
    if CIR=='oui' : 
        return CIR
    return(int(CIR))


generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
}



# -

import pandas as pd
import time
import shutil 

df = pd.read_csv('cir_data1.csv')
df

# +

# Dossier contenant les fichiers .txt
dossier_siren = "./dossier_siren"
dossier_traites = "./dossier_traites"  # Dossier où les fichiers traités seront déplacés

# Vérifier si le dossier traité existe, sinon le créer
os.makedirs(dossier_traites, exist_ok=True)


# Parcourir les fichiers .txt dans le dossier
for file_name in os.listdir(dossier_siren):
    if file_name.endswith(".txt"):
        print (file_name)
        # Extraire le siren et l'année depuis le nom du fichier
        parts = file_name.split('_')
        if len(parts) < 2:
            continue  # Ignorer les fichiers mal nommés
        siren = parts[0]
        
        # L'année est la première partie de la seconde partie (avant le tiret)
        annee = parts[1].split('-')[0]  # On prend la partie avant le tiret

        # Vérifier si l'année est dans l'intervalle 2016-2023
        if annee not in ["2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023"]:
            continue
        
        # Chemin complet du fichier
        file_path = os.path.join(dossier_siren, file_name)

        # Récupérer le montant CIR à partir du fichier
        cir_amount = generate(file_path)  # Assurez-vous que `generate()` est définie et retourne le montant CIR
        
        time.sleep(7)
        # Ajouter ou mettre à jour la ligne du DataFrame
        if siren not in df["siren"].values:
            # Utiliser pd.concat pour ajouter une nouvelle ligne si le SIREN n'est pas encore présent
            new_row = pd.DataFrame({"siren": [siren], f"{annee}_CIR": [cir_amount]})
            df = pd.concat([df, new_row], ignore_index=True)
        else:
            # Mettre à jour la valeur pour l'année correspondante
            df.loc[df["siren"] == siren, f"{annee}_CIR"] = cir_amount

        # Déplacer le fichier traité dans le dossier des fichiers traités
        shutil.move(file_path, os.path.join(dossier_traites, file_name))
        print(f"Fichier déplacé : {file_name} vers {dossier_traites}")




# +
df



# +
# Sauvegarder le DataFrame mis à jour dans le fichier CSV
df.to_csv('cir_data1.CSV', index=False)

print(f"Fichier '{'cir_data1.csv'}' mis à jour avec succès.")

# -
