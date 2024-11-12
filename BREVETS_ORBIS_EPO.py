# PATENT RETRIEVAL USING EPO API

# ATTENTION:
"""
1.  To use this code, it is necessary to have the Orbis database downloaded (`./resultados_patentes.csv`) 
    and the base with probable SIREN (`./probable_CIR_ETI_GE.csv`), both available on GitHub.

2.  You should enter the first SIREN digit you want in the section marked as # FILTERING FOR THE DIGIT YOU WANT.

3. You can even run it in different terminals, but you should save to different CSV files. Be careful with the 
   size of the loop to avoid retrieving duplicate patents, and then merge the two CSVs afterward.

   ex:
   csv1_path = "./BREVETS_siren7(1).csv"
   df1 = pd.read_csv(csv1_path, sep=';', dtype=str)

   csv2_path = "./BREVETS_siren7(2).csv"
   df2 = pd.read_csv(csv2_path, sep=';', dtype=str)

   df_combined = pd.concat([df1, df2], ignore_index=True)
   df_combined.to_csv("BREVETS_siren7.csv", index=False, sep=';')  
"""

# LIBRARY
import pandas as pd
import epo_ops
import xml.etree.ElementTree as ET
import os
import re
from requests.exceptions import ConnectionError


# LOADING ORBIS WITH ALL PATENTS
caminho_saida_csv = "./resultados_patentes.csv"
df_orbis_siren = pd.read_csv(caminho_saida_csv, delimiter=';', low_memory=False)


# LOADING PROBABLE SIREN
caminho_cir_data = "./probable_CIR_ETI_GE.csv"
df_cir_data = pd.read_csv(caminho_cir_data, delimiter=";",low_memory=False)
df_cir_data.columns = df_cir_data.columns.str.strip() 
df_cir_data['siren'] = df_cir_data['siren'].astype(str).str.zfill(9)
siren_list = df_cir_data['siren'].astype(str).tolist() 

# FILTERING FOR THE DIGIT YOU WANT (in this examples is 7)
siren_filtered = ['FR' + siren for siren in siren_list if siren.startswith(('7'))]
df_filtered = df_orbis_siren[df_orbis_siren['appl_bvdid'].isin(siren_filtered)]
df_filtered.reset_index(drop=True, inplace=True)


# CHOOSE THE NAME YOU WILL USE TO SAVE THE FOUND PATENTS IN CSV (in this case "BREVETS_siren7(1)")
csv_file_path = "./BREVETS_siren7(1).csv"
# Checking if the CSV file exists and load the data if it does.
if os.path.exists(csv_file_path):
    # Loading the existing DataFrame
    df_existente = pd.read_csv(csv_file_path, delimiter=';', low_memory=False)
else:
    df_existente = pd.DataFrame(columns=["SIREN", "Famille ID", "Brevet", "Date de Dépôt", "Année de Dépôt"])


# EPO KEY
# Davi
# client = epo_ops.Client(key="AhMvO8Kv17x0GszHaUnS9QGj8GVR92wU1ojTNEsFITirRLxL", secret="fgrznp1As3srmkG7k2TxAcAZBUXwp6F7MALDcRPy3pMNpldxADsJnH648NqytpUB")
# Eleonore
# client = epo_ops.Client(key="3jaNanovIV5o7Eqd8AWSD8nQeH78hGUM09eu4NkJVgXyXaGN", secret="mjlvVoogucXmwTWLQL6CnaoOlgcBhYkaqjX2nAoDJbYafdmUGHGgjBsXVgXBGewu")
# Davi 2
client = epo_ops.Client(key="tIQV3hg6ip0yqPy4mqAgynhzHrGsfklVAcen4yqJdAnWu6eK", secret="b2W0wFG7A2CuJX9THdiGpso0v3qkHuUgdLpI6hsYQzduopBY386AjNm8RC5BePzY")


# TAILLE DU FOR
start = 3765
end = 100000

for index, row in df_filtered.iloc[start:end].iterrows():

    # RESETTING RESULTS AT EACH ITERATION TO SAVE AT THE END
    resultados = []

    siren = row['appl_bvdid'][2:]  
    numero_patente = row['pub_nbr']  
    
    print(f"{index} {numero_patente}")

    # CHECK IF THE PATENT ALREADY EXISTS IN THE EXISTING DATAFRAME
    existing_row = df_existente[df_existente['Brevet'] == numero_patente]
    if not existing_row.empty: # df_existente already has the row
        if existing_row['Famille ID'].values[0] is not None and pd.notna(existing_row['Famille ID'].values[0]):
            print(f"   Existe déjà dans le fichier CSV avec une Famille ID valide.")
            continue  # Skip to the next iteration if the patent already exists and the Famille ID is valid.
        else:
            print(f"   Existe déjà dans le fichier CSV, mais Famille ID est manquant. Tentando novamente...")
            idx = existing_row.index[0]  # Getting the index of the first matching row.


    # FORMATTING PATENT NAME FOR API SEARCH
    codigo_pais = re.match(r'([A-Z]+)', numero_patente).group(1)
    remaining = numero_patente[len(codigo_pais):]  
    match = re.search(r'(\d+)([A-Z]{1,2}[0-9]?)', remaining) 
    if match:
        numero_docdb = match.group(1)
        tipo_demanda = match.group(2) if match.group(2) else ''
    else:
        numero_docdb = remaining
        tipo_demanda = ''


    try:
        # RETRIEVING PATENT INFORMATION FROM THE EPO API
        response = client.published_data(
            reference_type='publication',
            input=epo_ops.models.Docdb(numero_docdb, codigo_pais, tipo_demanda),
            endpoint='biblio',
        )

        # Process the response to extract the information
        if response.status_code == 200:
            data = response.text
            root = ET.fromstring(data)  

            # Navigate to the elements that contain the necessary information
            namespace = {'ops': 'http://ops.epo.org', 'default': 'http://www.epo.org/exchange'}

            # Getting the information
            famille_id = root.find('.//default:exchange-document', namespaces=namespace).get('family-id', 'N/A')
            date_depot = root.find('.//default:application-reference/default:document-id/default:date', namespaces=namespace).text if root.find('.//default:application-reference/default:document-id/default:date', namespaces=namespace) is not None else 'N/A'
            ano_depot = date_depot[:4] if date_depot != 'N/A' else 'N/A'

            # Updating or adding the results
            if existing_row.empty: # If it's a new patent
                resultados.append({
                    "SIREN": siren,
                    "Famille ID": famille_id,
                    "Brevet": numero_patente,
                    "Date de Dépôt": date_depot,
                    "Année de Dépôt": ano_depot
                })
            else:
                idx = existing_row.index[0]
                # Updating the existing row
                df_existente.at[idx, 'Famille ID'] = famille_id
                df_existente.at[idx, 'Date de Dépôt'] = date_depot
                df_existente.at[idx, 'Année de Dépôt'] = ano_depot

            if not existing_row.empty and famille_id == 'N/A':
                print(f"   {numero_patente} NOT found again, even with response = 200. Skip to the next iteration.")
                continue  # Skip to the next iteration if the patent already exists and the Famille ID is missing

        else:

            if not existing_row.empty and (existing_row['Famille ID'].values[0] is None or pd.isna(existing_row['Famille ID'].values[0])):
                print(f"{numero_patente} Not found again, response was NOT 200. Skip to the next iteration.")
                continue  # Skip to the next iteration if the patent already exists and the Famille ID is missing.

            # When the patent is not found
            print(f"   Erreur lors de la recherche du brevet {numero_patente}: {response.status_code} - {response.text}")
            resultados.append({
                "SIREN": siren,
                "Famille ID": None,
                "Brevet": numero_patente,
                "Date de Dépôt": None,
                "Année de Dépôt": None
            })

    except Exception as e:
        print(f"   Erreur lors du traitement du brevet {numero_patente}: {e}")
        if not existing_row.empty and (existing_row['Famille ID'].values[0] is None or pd.isna(existing_row['Famille ID'].values[0])):
            print(f"   {numero_patente} Not found again, raised EXCEPT. Skip to the next iteration.")
            continue  # Skip to the next iteration if the patent already exists and the Famille ID is missing

        # Add the available information, with blank fields.
        resultados.append({
            "SIREN": siren,
            "Famille ID": None,
            "Brevet": numero_patente,
            "Date de Dépôt": None,
            "Année de Dépôt": None
        })


    # Converting the found results into a DataFrame
    df_resultados = pd.DataFrame(columns=["SIREN", "Famille ID", "Brevet", "Date de Dépôt", "Année de Dépôt"])
    df_resultados = pd.DataFrame(resultados)


    # Checking if the 'Année de Dépôt' column exists and is not empty
    if 'Année de Dépôt' in df_resultados.columns and not df_resultados['Année de Dépôt'].empty:
        # Create columns for the years 2016 to 2024
        for year in range(2016, 2025):
            df_resultados[str(year)] = (df_resultados['Année de Dépôt'] == str(year)).astype(int)
    

    # FORMATTING COLUMNS
    # Try formatting the deposit date as dd/mm/yyyy, ignoring if the column does not exist
    try:
        df_resultados['Date de Dépôt'] = pd.to_datetime(df_resultados['Date de Dépôt'], errors='coerce').dt.strftime('%d/%m/%Y').where(df_resultados['Date de Dépôt'].notnull())
    except KeyError:
        print("   .")
    # Formatting SIREN
    if 'SIREN' in df_resultados.columns:  
        df_resultados['SIREN'] = df_resultados['SIREN'].str.zfill(9)  
        df_resultados['SIREN'] = df_resultados['SIREN'].str.replace(r'(\d{3})(\d{3})(\d{3})', r'\1 \2 \3', regex=True)  # Adicionar espaços
    # Check if the 'Famille ID' column exists before converting it in str
    if 'Famille ID' in df_resultados.columns:
        df_resultados['Famille ID'] = df_resultados['Famille ID'].astype(str)
    # Check if the 'Année de Dépôt' column exists before converting it
    if 'Année de Dépôt' in df_resultados.columns:
        df_resultados['Année de Dépôt'] = df_resultados['Année de Dépôt'].astype(str)


    # Add the new results to the existing DataFrame
    df_existente = pd.concat([df_existente, df_resultados], ignore_index=True)

    # Save the updated DataFrame to a CSV file
    df_existente.to_csv(csv_file_path, index=False, sep=';')
