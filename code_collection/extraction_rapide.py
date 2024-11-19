import pdfplumber
import re
import pytesseract
import os
from pdf2image import convert_from_path
import time
from pathlib import Path
import ocrmypdf
import pandas as pd
# Spécifiez le chemin d'accès à Tesseract
pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'

# +
import glob
df = pd.read_csv('probable_CIR_ETI_GE.csv', sep = ';', low_memory = False)

liste_siren = df['siren'][8549:].to_list()

# Dossier où se trouvent les fichiers PDF
dossier = './dossier_siren'  # Remplacez par le chemin réel

# Liste pour stocker les fichiers trouvés
fichiers_trouves = []

# Parcourir chaque SIREN dans la liste
for siren in liste_siren:
    # Utiliser glob pour trouver les fichiers commençant par le SIREN et terminant par .pdf
    fichiers = glob.glob(os.path.join(dossier, f"{siren}*.pdf"))
    
    # Ajouter les fichiers trouvés à la liste
    fichiers_trouves.extend(fichiers)


# -

def extraire_texte(pdf_file_path):
    texte_total = ""  # Initialiser une chaîne pour accumuler le texte
    with pdfplumber.open(pdf_file_path) as pdf:
        for page in pdf.pages:
            texte = page.extract_text()
            if texte:  # Vérifier si le texte a été extrait
                texte_total += texte  # Ajouter le texte de la page au texte total
    return texte_total  # Retourner le texte complet extrait


# +
def extraire_texte_avec_ocr(pdf_file_path):
    # Convertir les pages PDF en images
    pages = convert_from_path(pdf_file_path, poppler_path='/opt/homebrew/bin')

    # Texte total extrait du PDF
    texte_total = ""

    for page in pages:
        # Utiliser Tesseract pour extraire le texte de l'image
        texte = pytesseract.image_to_string(page, lang='fra')
        texte_total += texte + "\n"

    return texte_total




def extraire_texte_avec_ocr2(chemin_pdf):
    # Nom du fichier texte de sortie
    output_txt = os.path.splitext(chemin_pdf)[0] + ".txt"
    temp_pdf = "temp_with_ocr.pdf"  # Fichier PDF temporaire avec OCR intégré

    try:
        # Étape 1 : Appliquer OCR et créer un PDF avec couche texte
        ocrmypdf.ocr(chemin_pdf, temp_pdf, language='fra')
        print(f"OCR terminé pour {chemin_pdf}")

        # Étape 2 : Extraire le texte du PDF OCR avec pdfplumber
        with pdfplumber.open(temp_pdf) as pdf:
            with open(output_txt, 'w', encoding='utf-8') as txt_file:
                for page in pdf.pages:
                    texte = page.extract_text()
                    if texte:
                        txt_file.write(texte)
                        txt_file.write("\n")
        
        print(f"Extraction terminée, texte enregistré dans {output_txt}")
        return output_txt  # Retourne le chemin du fichier texte généré

    except Exception as e:
        print(f"Erreur de traitement pour {chemin_pdf} : {e}")
        return None

    finally:
        # Supprimer le fichier PDF temporaire
        if os.path.exists(temp_pdf):
            os.remove(temp_pdf)


# -

def extraire_texte_complet(pdf_file_path):
    """Extraire le texte complet en utilisant pdfplumber ou OCR si nécessaire."""
    texte = extraire_texte(pdf_file_path)
    
    # Condition pour déterminer si l'extraction est complète
    if not texte or len(texte.split()) < 100:  # Par exemple, moins de 100 mots
        print("Extraction incomplète, utilisation de l'OCR...")
        texte = extraire_texte_avec_ocr2(pdf_file_path)
    
    return texte

for fichier in fichiers_trouves: 
    print (fichier)
    texte = extraire_texte_complet(fichier)
    file_name = os.path.basename(fichier) 
    txt_name = os.path.splitext(file_name)[0] + '.txt' 
    txt_path = os.path.join('dossier_siren', txt_name)
    # Créer et ouvrir un fichier en mode écriture
    with open(txt_path, 'w') as fichier:
        # Écrire la chaîne dans le fichier
        fichier.write(texte)


