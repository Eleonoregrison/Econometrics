# DOWNLOAD COMPANY FINANCIAL REPORTS BY SIREN
# To use the code, you need the file `establishments_ETI_GE.csv` and a folder named `siren_folder` in the directory

# Required libraries
import pandas as pd
import requests
import json
import os
import time
from urllib3.exceptions import ConnectTimeoutError
from requests.exceptions import ConnectionError


# INPI Account credentials
#1
#username = "davi-lucena.souza@etu.minesparis.psl.eu"
#password = "020173ivadJanice@1"

#2
#username = "lucie.trolle@etu.minesparis.psl.eu"
#password = "Lucie@2002utiliseINPI"

#3
username = "davi_souza@usp.br"
password = "020173ivadJanice@1"

#4
#username = "souzadavilucena@gmail.com"
#password = "020173ivadJanice@1"

#5
#username = "souzaldavi00@gmail.com"
#password = "020173ivadJanice@1"


# Main logic
output_folder = "FinReports_siren"
siren_folder = 'probable_CIR_ETI_GE.csv'


# API URL
api_url = "https://registre-national-entreprises.inpi.fr/api/sso/login"

# Function to get token
def get_token(username, password):
    headers = {"Content-Type": "application/json"}
    data = {"username": username, "password": password}

    response = requests.post(api_url, json=data, headers=headers)

    if response.status_code == 200:
        return response.json()["token"]
    else:
        raise Exception(f"Authentication failed. Error code: {response.status_code}")

try:
    token = get_token(username, password)
    print(f"Token obtained: {token}")
except Exception as e:
    print(e)


# Function to regenerate token in case of error
def regenerate_token():
    print("Attempting to regenerate a new token...")
    try:
        return get_token(username, password)
    except Exception as e:
        print(f"Error while regenerating token: {str(e)}")
        return None


# Function to check if a file already exists to avoid re-downloading
def file_exists(file_path):
    return os.path.exists(file_path)


# Read SIRENs from a column in a DataFrame
df = pd.read_csv(siren_folder, sep=';', dtype={'siren_column': str}, low_memory=False)
def read_siren_list(dataframe, siren_column):
    # Ensures values are strings, removes nulls, and pads with leading zeros
    siren_list = dataframe[siren_column].dropna().astype(str).str.zfill(9).tolist()
    num_siren = len(siren_list)
    return siren_list, num_siren


# List documents and initiate download
def download_documents(siren, token, output_folder):
    url = f"https://registre-national-entreprises.inpi.fr/api/companies/{siren}/attachments"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        documents = response.json()
        for doc_type in ["bilans"]:
            for document in documents.get(doc_type, []):
                document_id = document["id"]
                document_closure_date = document["dateCloture"]
                filename = f"{siren}_{document_closure_date}.pdf"

                closure_year = int(document_closure_date[:4])
                if closure_year < 2016 or closure_year > 2023:
                    continue

                download_document(doc_type, document_id, filename, siren, token, output_folder)
    else:
        raise Exception(f"Failed to retrieve documents. Error code: {response.status_code}")


# Download a specific document by its ID
def download_document(doc_type, doc_id, filename, siren, token, output_folder):
    url = f"https://registre-national-entreprises.inpi.fr/api/{doc_type}/{doc_id}/download"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        print(f"\tDownloading document {filename}... ", end="")
        file_path = os.path.join(output_folder, filename)
        if file_exists(file_path):
            print("Document already exists. Skipping download.")
        else:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                with open(file_path, "wb") as pdf_file:
                    pdf_file.write(response.content)
                print("Downloaded successfully.")
            elif response.status_code == 404:
                print("Document not found.")
            elif response.status_code == 429:
                print("Rate limit reached. Retrying after a pause.")
                handle_rate_limit(response)
            else:
                raise Exception(f"Failed to download document. Error code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred while downloading the document: {str(e)}")


df.columns = df.columns.str.strip()
siren_list, num_siren = read_siren_list(df, 'siren')
print(f"{num_siren} SIRENs found in the file.")


# Start processing from a specific SIREN
# start_siren = "410129894"

processing_started = False

i = 1
for siren in siren_list:
    d += 1

    print(d)
    print(siren)
    print()
    if not siren.startswith('1'):
        continue

    # Start processing from a specific SIREN
    # if not processing_started:
        if siren == start_siren:
            processing_started = True
        else:
            continue     

    try:
        download_documents(siren, token, output_folder)
        time.sleep(1)
    except (ConnectTimeoutError, ConnectionError) as e:
        print(f"Error with SIREN {siren}: {str(e)}")
        print("Pausing for 30 minutes to restart and regenerate token...")
        time.sleep(1800)
        token = regenerate_token()
        if token:
            print(f"New token generated: {token}. Restarting process...")
            download_documents(siren, token, output_folder)
        else:
            print("Failed to regenerate token.")
            break
    except Exception as e:
        print(f"Error with SIREN {siren}: {str(e)}")
