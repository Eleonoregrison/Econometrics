# Libraries used
import os
import pdfplumber
import time
from google.cloud import vision
import io
import fitz  
from PIL import Image
import struct

# Add the path to the Google Cloud key (JSON file) with permission to use Google Vision
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./GVdigital-sprite-440813-b7-6369e6e0b606.json"

# Initialize the Google Vision API client
client = vision.ImageAnnotatorClient()

# Define the paths for the directories
folder_path = "FinReports_siren_PDF"  # Folder containing the PDF files
output_folder = "FinReports_siren_TXT"  # Folder where the TXT files will be saved
output_folder2 = "Processed_TXT" # Contains TXT files that have been read and processed using Gemini
tobig_folder = "Problems"  # Folder for files that take too long to process


# Create all the folders
# Create the 'FinReports_siren_TXT' folder if it doesn't exist yet
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
# Create the 'Processed_TXT' folder if it doesn't exist yet
if not os.path.exists(output_folder2):
    os.makedirs(output_folder2)
# Create the 'tobig' folder if it doesn't exist yet
if not os.path.exists(tobig_folder):
    os.makedirs(tobig_folder)


# List all PDF files in the input folder
file_paths = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith(".pdf")]


# Function to extract text from a PDF using pdfplumber
def extract_text(pdf_file_path):
    total_text = ""
    with pdfplumber.open(pdf_file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                total_text += text  
    return total_text  


# Function to extract text from a PDF using OCR (Google Vision) via PyMuPDF
def extract_text_with_ocr(pdf_file_path):
    total_text = ""

    # Open the PDF with PyMuPDF
    doc = fitz.open(pdf_file_path)

    # Process each page of the PDF
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        
        # Convert the page to an image (PixMap)
        pix = page.get_pixmap(dpi=150)
        img = Image.open(io.BytesIO(pix.tobytes("jpeg")))

        # Convert the image to bytes and send to Google Vision
        image_content = io.BytesIO()
        img.save(image_content, format='JPEG')
        image = vision.Image(content=image_content.getvalue())

        # Perform OCR on the image and organize text into lines and columns
        response = client.document_text_detection(image=image)

        # Collect all words with their positions
        words_with_positions = []
        for page in response.full_text_annotation.pages:
            for block in page.blocks:
                for paragraph in block.paragraphs:
                    for word in paragraph.words:
                        word_text = ''.join([symbol.text for symbol in word.symbols])
                        # Calculate the average y and x position of the word
                        word_x = sum([v.x for v in word.bounding_box.vertices]) / 4
                        word_y = sum([v.y for v in word.bounding_box.vertices]) / 4
                        words_with_positions.append((word_text, word_x, word_y))

        # Sort words first by the y position (line) and then by x (horizontal)
        words_with_positions.sort(key=lambda item: (item[2], item[1]))

        # Group words into logical lines
        line_text = ""
        previous_y = None
        for word, word_x, word_y in words_with_positions:
            # If the y difference is large, consider a new line
            if previous_y is not None and abs(word_y - previous_y) > 10:
                total_text += line_text.strip() + "\n"  # Add the complete line
                line_text = word  # Start a new line with the new word
            else:
                line_text += " " + word  # Continue on the same line

            previous_y = word_y  # Update the previous y position

        # Add the last line to the total text
        total_text += line_text.strip() + "\n"

    doc.close()
    return total_text


# Main function to extract complete text
def extract_complete_text(pdf_file_path):
    try:
        text = extract_text(pdf_file_path)
        if text:
            # If the text is incomplete or empty, use OCR
            if not text or len(text.split()) < 10000:
                print("    Incomplete extraction, using OCR...")
                text = extract_text_with_ocr(pdf_file_path)
            return text
    except struct.error as e:
        print(f"Error processing {pdf_file_path} with pdfplumber: {e}")

    print("    Incomplete extraction, using OCR...")
    return extract_text_with_ocr(pdf_file_path)


# Function to convert PDFs into TXT files     
def transform_pdfs_to_txt(file_paths, output_folder, output_folder2): 
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for i, file_path in enumerate(file_paths):
        txt_file_name = os.path.basename(file_path).replace(".pdf", ".txt")
        txt_file_path = os.path.join(output_folder, txt_file_name)
        txt_file_path1 = os.path.join(output_folder2, txt_file_name)

        if os.path.exists(txt_file_path) or os.path.exists(txt_file_path1):
            print(f"{i+1} file '{txt_file_path}' already exists.")
            continue

        print()
        print(f"{i+1} processing file: {file_path}")

        start_time = time.time()

        text = extract_complete_text(file_path)

        elapsed_time = time.time() - start_time

        if text is None:
            print(f"    The file {file_path} has pages that are too large, moving to 'tobig'")
            os.rename(file_path, os.path.join(tobig_folder, os.path.basename(file_path)))
            print(f"    ({elapsed_time:.0f} seconds)")
            print()
            continue

        with open(txt_file_path, "w", encoding="utf-8") as txt_file:
            txt_file.write(text)

        print(f"    File saved as {txt_file_path}")
        print(f"    ({elapsed_time:.0f} seconds)")
        print()


transform_pdfs_to_txt(file_paths, output_folder, output_folder2)
