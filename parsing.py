import pdfplumber
import re
import pytesseract
from pdf2image import convert_from_path
# Spécifiez le chemin d'accès à Tesseract
pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'


# +
def extraire_texte(pdf_file_path):
    texte_total = ""  # Initialiser une chaîne pour accumuler le texte
    with pdfplumber.open(pdf_file_path) as pdf:
        for page in pdf.pages:
            texte = page.extract_text()
            if texte:  # Vérifier si le texte a été extrait
                texte_total += texte  # Ajouter le texte de la page au texte total
    return texte_total  # Retourner le texte complet extrait


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


# -


def extraire_texte_complet(pdf_file_path):
    """Extraire le texte complet en utilisant pdfplumber ou OCR si nécessaire."""
    texte = extraire_texte(pdf_file_path)
    
    # Condition pour déterminer si l'extraction est complète
    if not texte or len(texte.split()) < 100:  # Par exemple, moins de 100 mots
        print("Extraction incomplète, utilisation de l'OCR...")
        texte = extraire_texte_avec_ocr(pdf_file_path)
    
    return texte


# Fonction pour extraire la valeur du crédit d'impôt recherche
def extraire_credit_impot_recherche2(texte):
    # Expression régulière pour trouver la phrase et capturer le montant
    match = re.search(r"crédit\s*(?:d(?:'|’)?\s*)?impôt recherche.*?([\d\s]+)\s*(euros|€)", texte, re.IGNORECASE)
    if match:
        montant = match.group(1)
        montant = montant.replace(' ', '')  # Retirer les espaces dans le montant
        return int(montant),f"Le montant du crédit d'impôt recherche est de {montant} €."

    return (0,"Crédit d'impôt recherche non trouvé dans le PDF.")



# Fonction pour extraire la valeur du crédit d'impôt recherche
def extraire_credit_impot_recherche(texte):
    # Expression régulière pour trouver la phrase et capturer le montant
    match = re.search(
        r"crédit\s*(?:d(?:'|’)?\s*)?impôt\s*(?:recherche|recherche et innovation).*?([\d\s,.]+)(k€|euros|€|€uros)", 
        texte, 
        re.IGNORECASE
    )
    
    if match:
        montant = match.group(1).replace('.', '')
        montant = montant.replace(' ', '')  # Retirer les espaces dans le montant
        unite = match.group(2).lower()  # Obtenir l'unité
        
        # Si l'unité est 'k€', multiplier par 1000
        if 'k€' in unite:
            montant = int(montant) * 1000
        else:
            montant = int(montant)
        
        return montant, f"Le montant du crédit d'impôt recherche est de {montant} €."

    return 0, "Crédit d'impôt recherche non trouvé dans le PDF."


file_paths = ["dossier_siren/30194011/bilans_301940011_2023-03-31_C_2023-07-18_65cb91bdf2a8d8428b04b07e.pdf", "dossier_siren/bilans_319557237_2018-12-31_C_2019-07-18_63e655f37e898005f50b2d79.pdf", "dossier_siren/bilans_324103829_2020-12-31_C_2021-06-22_63eaab83e79525b4a602615d.pdf", "dossier_siren/bilans_325230308_2023-03-31_C_2023-10-02_65ce16d4c740186270066ce2.pdf", "dossier_siren/bilans_326820065_2023-12-31_C_2024-06-14_66a21ec7205a3b0c120e5557.pdf", "dossier_siren/bilans_329822514_2023-12-31_C_2024-06-28_66ade495ea54f8771703b84c.pdf", "dossier_siren/bilans_330076159_2023-12-31_C_2024-06-13_669719434b3dd85ac2073840.pdf", "dossier_siren/bilans_333275774_2023-12-31_C_2024-06-27_66a231d0dd8463e4210e3104.pdf"]

# +
texte = extraire_texte_complet(file_paths[0])

extraire_credit_impot_recherche(texte)
# -

# Pour le 4e, il est noté crédit impôt recherche et innovation. Est-ce qu'on le prend en compte ? \
# Comment faire si c'est dans un tableau ? ex : 5e fichier de la liste\
# Dans l'exemple 6, la somme est arrondie. \
# A chaque nouveau document j'ajoute un cas -> est-ce qu'on peut généraliser ?\
# Critère pour passer à l'OCR : moins de 100 mots \
# Bilan : bilans_331408336_2023-12-31_K_2024-07-03_669911e4b0f64ccc0d04b552.pdf c'est dans une ligne d'un tableau

# +
#Ouvrir un tableau 
# Chemin vers votre fichier PDF

pdf_file_path = "dossier_siren/bilans_331408336_2023-12-31_K_2024-07-03_669911e4b0f64ccc0d04b552.pdf"

# Ouvrir le PDF et extraire les tableaux
with pdfplumber.open(pdf_file_path) as pdf:
    for page in pdf.pages:
        # Extraire tous les tableaux de la page
        tables = page.extract_tables()
        
        for table in tables:
            # Afficher le contenu du tableau
            for row in table:
                print(row)  # Chaque row est une liste contenant les valeurs des cellules
# -


