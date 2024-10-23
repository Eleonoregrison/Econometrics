# TRANSFORMER DES FICHIERS PDF EN TXT

import os
import pdfplumber
import re
import pytesseract
from pdf2image import convert_from_path

# Spécifie le chemin Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# Chemin du dossier où se trouvent les PDF
folder_path = r"probable_siren7"

# Liste tous les fichiers contenus dans le dossier
file_paths = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith(".pdf")]

# Nom du dossier dans lequel les fichiers txt seront stockés
output_folder = r"pasta_txt"


def extraire_texte(pdf_file_path):
    # Extraire le texte à l'aide de pdfplumber
    texte_total = ""  
    with pdfplumber.open(pdf_file_path) as pdf:
        for page in pdf.pages:
            texte = page.extract_text()
            if texte:
                texte_total += texte  
    return texte_total  

def extraire_texte_avec_ocr(pdf_file_path):
    # Extraction de texte à l'aide de l'OCR (Tesseract)
    pages = convert_from_path(pdf_file_path, poppler_path=r"D:\AE\COURS\TR\Code&Data_TR\poppler-24.08.0\Library\bin")
    texte_total = ""
    for page in pages:
        texte = pytesseract.image_to_string(page, lang='fra')
        texte_total += texte + "\n"
    return texte_total

def extraire_texte_complet(pdf_file_path):
    # Extraction du texte intégral à l'aide de pdfplumber ou de l'OCR si nécessaire
    texte = extraire_texte(pdf_file_path)
    if not texte or len(texte.split()) < 100:
        print("Extraction incomplète, utilisation de l'OCR...")
        texte = extraire_texte_avec_ocr(pdf_file_path)
    return texte


# Fonction d'extraction de la valeur du crédit d'impôt recherche
'''
def extraire_credit_impot_recherche(texte):
    match = re.search(
        r"crédit\s*(?:d(?:'|’)?\s*)?impôt\s*(?:recherche|recherche et innovation).*?([\d\s,.]+)(k€|euros|€|€uros)", 
        texte, 
        re.IGNORECASE
    )
    if match:
        montant = match.group(1).replace('.', '').replace(' ', '')  
        unite = match.group(2).lower()  
        if 'k€' in unite:
            montant = int(montant) * 1000
        else:
            montant = int(montant)
        return montant, f"Le montant du crédit d'impôt recherche est de {montant} €."
    return 0, "Crédit d'impôt recherche non trouvé dans le PDF."

# Fonction permettant de traiter plusieurs fichiers et d'afficher les résultats
def processar_arquivos(file_paths):
    for i, file_path in enumerate(file_paths):
        print(f"Processando arquivo {i+1}: {file_path}")
        texte = extraire_texte_complet(file_path)
        resultado, mensagem = extraire_credit_impot_recherche(texte)
        if resultado == 0:
            print(f"Arquivo {i+1}: {mensagem}")  # Imprime que le CIR n'a pas été trouvé
        else:
            print(f"Arquivo {i+1}: {mensagem}")  # Imprime la valeur CIR trouvée
'''

# Fonction de transformation des PDF en fichiers TXT
def transformar_pdf_em_txt(file_paths, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)  # Créer le dossier s'il n'existe pas
    
    for i, file_path in enumerate(file_paths):
        
        # Crée le chemin du fichier .txt correspondant
        txt_file_name = os.path.basename(file_path).replace(".pdf", ".txt")
        txt_file_path = os.path.join(output_folder, txt_file_name)

        # Vérifier si le fichier .txt existe déjà
        if os.path.exists(txt_file_path):
            print(f"Fichier {txt_file_path} existe déjà.")
            continue  

        print(f"Traitement d'un fichier {i+1}: {file_path}")
        texte = extraire_texte_complet(file_path)

        # Salva o texto em um arquivo .txt
        with open(txt_file_path, "w", encoding="utf-8") as txt_file:
            txt_file.write(texte)
        
        print(f"Fichier {i+1} enregistré comme {txt_file_path}")


transformar_pdf_em_txt(file_paths, output_folder)
