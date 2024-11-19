import os
import time
import pandas as pd
import shutil
from google.cloud import aiplatform
import vertexai
from vertexai.generative_models import GenerativeModel, Part, SafetySetting

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"D:\AE\COURS\TR\Code&Data_TR\digital-sprite-440813-b7-a650a7146c9c.json"  # Remplacer par votre clé 

# Tente ler o arquivo CSV ou cria um DataFrame vazio se o arquivo não existir
try:
    df = pd.read_csv('cir_data1.csv')
except FileNotFoundError:
    df = pd.DataFrame(columns=['siren'])
    df.to_csv('cir_data1.csv', index=False)
    print("Arquivo 'cir_data1.csv' criado com sucesso.")

def open_file(file_path): 
    with open(file_path, "r", encoding="utf-8") as fichier:
        contenu = fichier.read()
    return contenu

def generate(file_path):
    CIR = ""
    contenu = open_file(file_path)
    vertexai.init(project="digital-sprite-440813-b7", location="us-central1")
    model = GenerativeModel("gemini-1.5-flash-002")

    safety_settings = None

    # Tentativas de geração com tratamento para erro 429
    while True:
        try:
            responses = model.generate_content(
                [f"""Quel est le montant en euros de Crédit Impôt Recherche (CIR) reçu par l\'entreprise au cours de l'année du bilan dans le document suivant {contenu}? Faire attention car le montant peut être écrit en milliers d'euros (k€) il faudra alors faire la conversion en euros. Si le montant est négatif, il faudra alors prendre sa valeur opposée positive. Faire attention à ne pas retourner le montant du Crédit d'Impôt pour la Compétitivité de l'Emploi (CICE) qui ne nous intéresse pas. Retourner uniquement le montant sans explications et sans unités. Si l'entreprise reçoit du CIR mais ne précise pas combien, renvoyer 'oui'. Si aucun CIR n'est perçu ou qu'aucune information concernat le CIR n'est mentionnée, renvoyer 0. 
                """
            ],
                generation_config=generation_config,
                safety_settings=safety_settings,
                stream=True,
            )

            for response in responses:
                CIR += response.text 
                CIR = CIR.replace('\n', '')
            if CIR == 'oui': 
                return CIR
            return float(CIR)

        except Exception as e:
            if "Resource exhausted" in str(e):
                print("Limite de recurso atingida. Esperando 5 minutos antes de tentar novamente...")
                time.sleep(300)  # Espera por 5 minutos
            else:
                raise  # Lança novamente a exceção se não for um erro de recurso

generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
}

# Dossier contenant les fichiers .txt
dossier_siren = "./pasta_txt"
dossier_traites = "./dossier_traites"  # Dossier onde os arquivos tratados serão movidos

# Vérifier si le dossier traité existe, sinon le créer
os.makedirs(dossier_traites, exist_ok=True)

# Parcourir les fichiers .txt dans le dossier
for file_name in os.listdir(dossier_siren):
    if file_name.endswith(".txt"):
        print(file_name)
        parts = file_name.split('_')
        if len(parts) < 2:
            continue  # Ignorer os arquivos mal nomeados
        siren = int(parts[0])
        annee = parts[1].split('-')[0]

        if annee not in ["2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023"]:
            continue
        
        file_path = os.path.join(dossier_siren, file_name)

        # Récupérer le montant CIR à partir du fichier
        cir_amount = generate(file_path)
        
        time.sleep(7)
        if siren not in df["siren"].values:
            new_row = pd.DataFrame({"siren": [siren], f"{annee}_CIR": [cir_amount]})
            df = pd.concat([df, new_row], ignore_index=True)
        else:
            df.loc[df["siren"] == siren, f"{annee}_CIR"] = cir_amount

        shutil.move(file_path, os.path.join(dossier_traites, file_name))
        print(f"Fichier déplacé : {file_name} vers {dossier_traites}")

# Sauvegarder le DataFrame mis à jour dans le fichier CSV
df.to_csv('cir_data1.csv', index=False)

print(f"Fichier '{'cir_data1.csv'}' mis à jour com sucesso.")
