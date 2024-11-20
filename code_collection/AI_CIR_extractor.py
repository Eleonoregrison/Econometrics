import os
import time
import pandas as pd
import shutil
from google.cloud import aiplatform
import vertexai
from vertexai.generative_models import GenerativeModel, Part, SafetySetting


# Replace with your key with Google Vertex AI permision
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./digital-sprite-440813-b7-a650a7146c9c.json"   

# Folder containing .txt files
siren_folder = "FinReports_siren_TXT"
processed_folder = "Processed_TXT"  # Folder where processed files will be moved
# Check if the processed folder exists, if not create it
os.makedirs(processed_folder, exist_ok=True)

# Path to the CSV with the CIR amount
output_CSV = "cir_data22.csv"

# Try to read the CSV file or create an empty DataFrame if the file doesn't exist
try:
    df = pd.read_csv(output_CSV)
except FileNotFoundError:
    df = pd.DataFrame(columns=['siren'])
    df.to_csv(output_CSV, index=False)
    print("File for output created successfully.")

def open_file(file_path): 
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    return content


def generate(file_path):
    CIR = ""
    content = open_file(file_path)
    vertexai.init(project="digital-sprite-440813-b7", location="us-east5") # Replace the project name with the one from your Google Cloud account
    model = GenerativeModel("gemini-1.5-flash-002")

    safety_settings = None
 
    # Generation attempts with handling for error 429
    while True:
        try:
            responses = model.generate_content(
                [f"""Quel est le montant en euros de Crédit Impôt Recherche (CIR) reçu par l\'entreprise au cours de l'année du bilan dans le document suivant {content}? Faire attention car le montant peut être écrit en milliers d'euros (k€) il faudra alors faire la conversion en euros. Si le montant est négatif, il faudra alors prendre sa valeur opposée positive. Faire attention à ne pas retourner le montant du Crédit d'Impôt pour la Compétitivité de l'Emploi (CICE) qui ne nous intéresse pas. Retourne uniquement le montant, sans explications ni réponse complète, juste le chiffre, sans unités, sans unité monétaire et sans espaces entre les chiffres. Assurez-vous de renvoyer le nombre avec un point comme séparateur décimal, sans utiliser de virgule. Si l'entreprise reçoit du CIR mais ne précise pas combien, renvoyer 'oui'. Si aucun CIR n'est perçu ou qu'aucune information concernat le CIR n'est mentionnée, renvoyer 0."""],
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
                print("Resource limit reached. Waiting 30 seconds before trying again...")
                time.sleep(30)  # Wait for 30 seconds
            else:
                raise  # Re-raise the exception if it's not a resource error

generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
}


# Iterate through .txt files in the folder
for file_name in os.listdir(siren_folder):
    if file_name.endswith(".txt"):
        print(file_name)
        parts = file_name.split('_')
        if len(parts) < 2:
            continue  # Skip poorly named files
        siren = int(parts[0])
        year = parts[1].split('-')[0]

        if year not in ["2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023"]:
            continue
        
        file_path = os.path.join(siren_folder, file_name)

        # Retrieve the CIR amount from the file
        cir_amount = generate(file_path)
        
        time.sleep(2)
        if siren not in df["siren"].values:
            new_row = pd.DataFrame({"siren": [siren], f"{year}_CIR": [cir_amount]})
            df = pd.concat([df, new_row], ignore_index=True)
        else:
            df.loc[df["siren"] == siren, f"{year}_CIR"] = cir_amount

        shutil.move(file_path, os.path.join(processed_folder, file_name))
        print(f"File moved: {file_name} to {processed_folder}")

        # Save the updated DataFrame to the CSV file
        df.to_csv(output_CSV, index=False)

        print(f"File '{output_CSV}' updated successfully.")

