# Bibliothèque utilisée
import os
import pdfplumber
import time
from pdf2image import convert_from_path
from google.cloud import vision
import io
import fitz  # PyMuPDF
from PIL import Image

# Configuração do caminho da credencial do Google Cloud
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"D:\AE\COURS\TR\Code&Data_TR\chave_API_GOOGLE\robust-haiku-439710-j3-938c005f046f.json"

# Inicializa o cliente da API Google Vision
client = vision.ImageAnnotatorClient()

# Definir os caminhos dos diretórios
folder_path = r"probable_siren4"  # Dossier contenant les fichiers PDF
output_folder = r"pasta_txt"  # Dossier où les fichiers TXT seront enregistrés
tobig_folder = r"tobig"  # Dossier pour les fichiers qui prennent trop de temps à traiter

# Créer le dossier 'tobig' s'il n'existe pas encore
if not os.path.exists(tobig_folder):
    os.makedirs(tobig_folder)

# Liste de tous les fichiers PDF dans le dossier d'entrée
file_paths = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith(".pdf")]

# Fonction pour extraire le texte d'un PDF avec pdfplumber
def extraire_texte(pdf_file_path):
    texte_total = ""
    with pdfplumber.open(pdf_file_path) as pdf:
        for page in pdf.pages:
            texte = page.extract_text()
            if texte:
                texte_total += texte  
    return texte_total  

# Fonction pour extraire le texte d'un PDF en utilisant l'OCR (Google Vision)
def extraire_texte_avec_ocr(pdf_file_path):
    texte_total = ""

    # Abre o PDF com PyMuPDF
    doc = fitz.open(pdf_file_path)

    # Processa cada página do PDF
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        
        # Converte a página para imagem (PixMap)
        pix = page.get_pixmap()
        img = Image.open(io.BytesIO(pix.tobytes("jpeg")))

        # Converte a imagem para bytes e envia ao Google Vision
        image_content = io.BytesIO()
        img.save(image_content, format='JPEG')
        image = vision.Image(content=image_content.getvalue())

        # Realiza OCR na imagem e organiza o texto em linhas e colunas
        response = client.document_text_detection(image=image)

        # Coleta todas as palavras com suas posições
        words_with_positions = []
        for page in response.full_text_annotation.pages:
            for block in page.blocks:
                for paragraph in block.paragraphs:
                    for word in paragraph.words:
                        word_text = ''.join([symbol.text for symbol in word.symbols])
                        # Calcula a posição média y e x da palavra
                        word_x = sum([v.x for v in word.bounding_box.vertices]) / 4
                        word_y = sum([v.y for v in word.bounding_box.vertices]) / 4
                        words_with_positions.append((word_text, word_x, word_y))

        # Ordena as palavras primeiro pela posição y (linha) e depois pela posição x (horizontal)
        words_with_positions.sort(key=lambda item: (item[2], item[1]))

        # Agrupa as palavras em linhas lógicas
        line_text = ""
        previous_y = None
        for word, word_x, word_y in words_with_positions:
            # Se a diferença de y for grande, considera uma nova linha
            if previous_y is not None and abs(word_y - previous_y) > 10:
                texte_total += line_text.strip() + "\n"  # Adiciona a linha completa
                line_text = word  # Começa uma nova linha com a nova palavra
            else:
                line_text += " " + word  # Continua na mesma linha

            previous_y = word_y  # Atualiza a posição y anterior

        # Adiciona a última linha ao texto total
        texte_total += line_text.strip() + "\n"

    doc.close()  # Fecha o documento PDF
    return texte_total
#"""

# Fonction pour vérifie si toutes les pages du PDF sont de taille acceptable
def taille_des_pages(pdf_file_path, limite_largura=842, limite_altura=1190):
    with pdfplumber.open(pdf_file_path) as pdf:
        for page in pdf.pages:
            largura, altura = page.width, page.height
            if largura > limite_largura or altura > limite_altura:
                return False
    return True

# Fonction principale pour extraire le texte complet
def extraire_texte_complet(pdf_file_path):
    texte = extraire_texte(pdf_file_path)
    # Si le texte est incomplet ou vide utiliser l'OCR
    if not texte or len(texte.split()) < 1000000:
        print("    Extraction incomplète, utilisation de l'OCR...")
        # Vérifier la taille des pages
        if not taille_des_pages(pdf_file_path):
            return None
        texte = extraire_texte_avec_ocr(pdf_file_path)
    return texte

# Fonction de transformation des PDF en fichiers TXT
def transformer_pdf_em_txt(file_paths, output_folder): 
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for i, file_path in enumerate(file_paths):
        txt_file_name = os.path.basename(file_path).replace(".pdf", ".txt")
        txt_file_path = os.path.join(output_folder, txt_file_name)

        if os.path.exists(txt_file_path):
            print(f"{i+1} fichier '{txt_file_path}' existe déjà.")
            continue

        print()
        print(f"{i+1} fichier en traitement: {file_path}")

        start_time = time.time()

        texte = extraire_texte_complet(file_path)

        elapsed_time = time.time() - start_time

        if texte is None:
            print(f"    Le fichier {file_path} a des pages trop grandes, déplacement vers 'tobig'")
            os.rename(file_path, os.path.join(tobig_folder, os.path.basename(file_path)))
            print(f"    ({elapsed_time:.0f} secondes)")
            print()
            continue

        with open(txt_file_path, "w", encoding="utf-8") as txt_file:
            txt_file.write(texte)

        print(f"    Fichier enregistré comme {txt_file_path}")
        print(f"    ({elapsed_time:.0f} secondes)")
        print()

transformer_pdf_em_txt(file_paths, output_folder)
