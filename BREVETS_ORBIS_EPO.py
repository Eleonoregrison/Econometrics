
import pandas as pd

caminho_saida_csv = "./resultados_patentes.csv"  # CSV is in DRIVE

# Carregar o arquivo CSV em um DataFrame
df_orbis_siren = pd.read_csv(caminho_saida_csv, delimiter=';', low_memory=False)

# Exibir o resultado
df_orbis_siren

#
# Now I filtered the base to the Sirens that I want 
# Obter a lista de SIRENs do DataFrame cir_dataEPO
caminho_cir_data = "./probable_CIR_ETI_GE.csv"  # Substitua pelo caminho do arquivo correto
df_cir_data = pd.read_csv(caminho_cir_data, low_memory=False)

siren_list = df_cir_data['siren'].astype(str).tolist() # Make a siren_list using this df_cir_data1

# Criar um conjunto de SIRENs que começam com 5 e adicionar "FR" na frente
siren_filtered = ['FR' + siren for siren in siren_list if siren.startswith(('5'))] # Filter the the ones who starts with 5

# Filtrar o DataFrame df_orbis_siren para manter apenas as linhas com appl_bvdid em siren_filtered
df_filtered = df_orbis_siren[df_orbis_siren['appl_bvdid'].isin(siren_filtered)]

# Salvar o DataFrame filtrado como CSV
caminho_saida_csv = "./df_filtered.csv"  # Atualize com o caminho de saída desejado
df_filtered.to_csv(caminho_saida_csv, index=False)
df_filtered.reset_index(drop=True, inplace=True)


# BIBLIOTECA
import pandas as pd
import epo_ops
import xml.etree.ElementTree as ET
import os
import re


# PATENTES DO 5
caminho_saida_csv = "./df_filtered.csv"
df_filtered = pd.read_csv(caminho_saida_csv, delimiter=';', low_memory=False)
df_filtered.reset_index(drop=True, inplace=True)


# CHAVE EPO
# Davi
# client = epo_ops.Client(key="AhMvO8Kv17x0GszHaUnS9QGj8GVR92wU1ojTNEsFITirRLxL", secret="fgrznp1As3srmkG7k2TxAcAZBUXwp6F7MALDcRPy3pMNpldxADsJnH648NqytpUB")
# Eleonore
client = epo_ops.Client(key="3jaNanovIV5o7Eqd8AWSD8nQeH78hGUM09eu4NkJVgXyXaGN", secret="mjlvVoogucXmwTWLQL6CnaoOlgcBhYkaqjX2nAoDJbYafdmUGHGgjBsXVgXBGewu")

# CSV where they will be saved
csv_file_path = "./BREVETS_siren5.csv"


# Verificar se o arquivo CSV existe e carregar os dados, se existir
if os.path.exists(csv_file_path):
    df_existente = pd.read_csv(csv_file_path, delimiter=';', low_memory=False)
else:
    df_existente = pd.DataFrame(columns=["SIREN", "Famille ID", "Brevet", "Date de Dépôt", "Année de Dépôt"])


# TAILLE DU FOR
start = 0
interval = 10000

for index, row in df_filtered.iloc[start:(start+interval)].iterrows():

    # RESETANDO RESULTADOS
    resultados = []

    # PEGANDO SIRENE E PATENTE DA DF PATENTES DO 9 (df_filtered)
    siren = row['appl_bvdid'][2:]  
    numero_patente = row['pub_nbr']  
    
    # PRINTANDO INDEX DA LINHA DA DF PATENTES DO 9 E A PATENTE
    print(f"{index} {numero_patente}")
    
    # Verificar se a patente já existe no DataFrame existente
    existing_row = df_existente[df_existente['Brevet'] == numero_patente]
    
    if not existing_row.empty: # df_existente já possui a linha
        if existing_row['Famille ID'].values[0] is not None and pd.notna(existing_row['Famille ID'].values[0]):
            print(f"   Existe déjà dans le fichier CSV avec une Famille ID valide.")
            continue  # Pula para a próxima iteração se a patente já existir e Famille ID for válido
        else:
            print(f"   Existe déjà dans le fichier CSV, mais Famille ID est manquant. Tentando novamente...")
            idx = existing_row.index[0]  # Pegando o índice da primeira linha correspondente

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
        # Buscar informações da patente na API do EPO
        response = client.published_data(
            reference_type='publication',
            input=epo_ops.models.Docdb(numero_docdb, codigo_pais, tipo_demanda),
            endpoint='biblio',
        )

        # Processar a resposta para extrair as informações
        if response.status_code == 200:
            data = response.text
            root = ET.fromstring(data)  # Analisar o XML

            # Navegue até os elementos que contêm as informações necessárias
            namespace = {'ops': 'http://ops.epo.org', 'default': 'http://www.epo.org/exchange'}

            # Obtendo as informações
            famille_id = root.find('.//default:exchange-document', namespaces=namespace).get('family-id', 'N/A')
            date_depot = root.find('.//default:application-reference/default:document-id/default:date', namespaces=namespace).text if root.find('.//default:application-reference/default:document-id/default:date', namespaces=namespace) is not None else 'N/A'

            # Extraindo o ano da data de depósito
            ano_depot = date_depot[:4] if date_depot != 'N/A' else 'N/A'

            # Atualizando ou adicionando os resultados
            if existing_row.empty: # se for patente nova
                resultados.append({
                    "SIREN": siren,
                    "Famille ID": famille_id,
                    "Brevet": numero_patente,
                    "Date de Dépôt": date_depot,
                    "Année de Dépôt": ano_depot
                })
            else:
                idx = existing_row.index[0]
                # Atualizando a linha existente
                df_existente.at[idx, 'Famille ID'] = famille_id
                df_existente.at[idx, 'Date de Dépôt'] = date_depot
                df_existente.at[idx, 'Année de Dépôt'] = ano_depot

            if not existing_row.empty and famille_id == 'N/A':
                print(f"   {numero_patente} não foi encontrada denovo, mesmo sendo response = 200. Pula para a próxima iteração.")
                continue  # Pula para a próxima iteração se a patente já existir e Famille ID estiver ausente

        else:

            if not existing_row.empty and (existing_row['Famille ID'].values[0] is None or pd.isna(existing_row['Famille ID'].values[0])):
                print(f"{numero_patente} não foi encontrada denovo, response NÃO FOI 200. Pula para a próxima iteração.")
                continue  # Pula para a próxima iteração se a patente já existir e Famille ID estiver ausente

            # Quando a patente não é encontrada
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
            print(f"   {numero_patente} não foi encontrada denovo, deu EXCEPT. Pula para a próxima iteração.")
            continue  # Pula para a próxima iteração se a patente já existir e Famille ID estiver ausente

        # Adiciona as informações disponíveis, com campos em branco
        resultados.append({
            "SIREN": siren,
            "Famille ID": None,
            "Brevet": numero_patente,
            "Date de Dépôt": None,
            "Année de Dépôt": None
        })

    # Zerando o DataFrame
    df_resultados = pd.DataFrame(columns=["SIREN", "Famille ID", "Brevet", "Date de Dépôt", "Année de Dépôt"])
    
    # Criar um DataFrame com os resultados
    df_resultados = pd.DataFrame(resultados)

    # Verifique se a coluna 'Année de Dépôt' existe e não está vazia
    if 'Année de Dépôt' in df_resultados.columns and not df_resultados['Année de Dépôt'].empty:
        # Criar colunas para os anos de 2016 a 2024
        for year in range(2016, 2025):
            df_resultados[str(year)] = (df_resultados['Année de Dépôt'] == str(year)).astype(int)
    
    # Tentar formatar a data de depósito como dd/mm/aaaa, ignorando se a coluna não existir
    try:
        df_resultados['Date de Dépôt'] = pd.to_datetime(df_resultados['Date de Dépôt'], errors='coerce').dt.strftime('%d/%m/%Y').where(df_resultados['Date de Dépôt'].notnull())
    except KeyError:
        print("   .")
    
    # Salvar o DataFrame atualizado em um arquivo CSV, formatando o SIREN
    if 'SIREN' in df_resultados.columns:  # Verifique se a coluna SIREN existe
        df_resultados['SIREN'] = df_resultados['SIREN'].str.zfill(9)  # Preencher com zeros à esquerda
        df_resultados['SIREN'] = df_resultados['SIREN'].str.replace(r'(\d{3})(\d{3})(\d{3})', r'\1 \2 \3', regex=True)  # Adicionar espaços

    # Verifica se a coluna 'Famille ID' existe antes de convertê-la
    if 'Famille ID' in df_resultados.columns:
        df_resultados['Famille ID'] = df_resultados['Famille ID'].astype(str)

    # Verifica se a coluna 'Année de Dépôt' existe antes de convertê-la
    if 'Année de Dépôt' in df_resultados.columns:
        df_resultados['Année de Dépôt'] = df_resultados['Année de Dépôt'].astype(str)

    # Adicionar os novos resultados ao DataFrame existente
    df_existente = pd.concat([df_existente, df_resultados], ignore_index=True)

    # Salvar o DataFrame atualizado em um arquivo CSV
    df_existente.to_csv(csv_file_path, index=False, sep=';')
