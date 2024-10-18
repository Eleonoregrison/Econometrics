import pandas as pd
import requests
import json
import os

username = "davi-lucena.souza@etu.minesparis.psl.eu"
password = "020173ivadJanice@1"

url = "https://registre-national-entreprises.inpi.fr/api/sso/login"

# Connexion API et obtention token
def collecte_token(username, password):
    headers = {"Content-Type": "application/json"}
    data = {"username": username, "password": password}
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()["token"]
    else:
        raise Exception(f"Échec de l'authentification. Code d'erreur : {response.status_code}")


try:
    token = collecte_token(username, password)
    print(f"Token obtido: {token}")
except Exception as e:
    print(e)


# Função para verificar se o arquivo já existe no diretório
def fichier_existe(chemin_fichier):
    return os.path.exists(chemin_fichier)


# Lecture des SIREN à interroger à partir d'une colonne d'un DataFrame
df = pd.read_csv('etablissements_ETI_GE.csv', dtype={'colonne_siren': str}, low_memory=False)

def lecture_liste_siren(dataframe, colonne_siren):
    # Garante que os valores sejam strings, remove nulos e preenche com zeros à esquerda
    liste_siren = dataframe[colonne_siren].dropna().astype(str).str.zfill(9).tolist()
    nb_siren = len(liste_siren)
    return liste_siren, nb_siren


# Liste les documents et lance leur téléchargement
def telecharge_documents(siren, token, dossier_siren):
    # Paramètres requête API
    url = f"https://registre-national-entreprises.inpi.fr/api/companies/{siren}/attachments"
    headers = {"Authorization": f"Bearer {token}"}
    # Interroge le serveur INPI
    response = requests.get(url, headers=headers)
    # Statut API ok...
    if response.status_code == 200:
        # Collecte liste des documents disponibles au téléchargement
        documents = response.json()
        # Passe en revue tous les documents disponibles pour éventuel téléchargement
        for document_type in ["bilans"]:
            for document in documents.get(document_type, []):
                document_id = document["id"]
                document_date_depot = document["dateDepot"]
                match document_type:
                    case "bilans":
                        document_type_bilan = document["typeBilan"]
                        document_date_cloture = document["dateCloture"]
                        if document_date_cloture and document_date_cloture.startswith("2023"):
                            nom_fichier = f"{document_type}_{siren}_{document_date_cloture}_{document_type_bilan}_{document_date_depot}.pdf"

                            telecharge_document(document_type, document_id, nom_fichier, siren, token, dossier_siren)
                        else:
                            print(f"Le document avec ID {document_id} n'a pas de dateCloture ou n'est pas de 2023.")
                    case _:
                         print(f"Type de document non géré : {document_type}")
    # ... ou Statut API = erreur
    else:
        raise Exception(f"Échec de la récupération des documents. Code d'erreur : {response.status_code}")

# Télécharge un document à partir de son identifiant
def telecharge_document(document_type, document_id, nom_fichier, siren, token, dossier_siren):
    # Paramètres requête API
    url = f"https://registre-national-entreprises.inpi.fr/api/{document_type}/{document_id}/download"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        # Affiche le nom du fichier en cours
        message=f"\tDocument {nom_fichier} : "
        message_complet=message
        print(message,end="")
        # Vérifie si le fichier existe déjà
        # Si existe déjà : affiche le message "Le document existe déjà. Téléchargement abandonné..."...
        chemin_fichier = os.path.join(dossier_siren, nom_fichier)
        if fichier_existe(chemin_fichier):
            message="Le document existe déjà. Téléchargement abandonné..."
            message_complet=message_complet + message
            print(message)
        # ... sinon interrogation de L'API
        else:
            # Interroge le serveur INPI
            response = requests.get(url, headers=headers)
            # Statut API ok
            if response.status_code == 200:
                # Sauvegarde le contenu dans le dossier correspondant au SIREN
                with open(chemin_fichier, "wb") as pdf_file:
                    pdf_file.write(response.content)
                    message="Le document est téléchargé."
                    message_complet=message_complet + message
                    print(message)
            elif response.status_code == 404:
                message="Le document n'a pas été trouvé."
                message_complet=message_complet + message
                print(message)
            else:
                message=f"Échec du téléchargement du document. Code d'erreur : {response.status_code}"
                message_complet=message_complet + message
                raise Exception(message)
        journalisation_message(siren, message_complet, dossier_siren)
    except Exception as e:
        message=f"Une exception s'est produite lors du téléchargement du document : {str(e)}"
        message_complet=message_complet + message
        print(message)
        journalisation_message(siren, message_complet, dossier_siren)

# Journalisation des messages
def journalisation_message(siren, message, dossier_siren):
    nom_fichier_journalisation = f"Journalisation_API_INPI_{siren}.txt"
    chemin_journalisation = os.path.join(dossier_siren, nom_fichier_journalisation)
    
    # Test existence du fichier de journalisation
    fichier_existe = os.path.exists(chemin_journalisation)
    # Ouverture fichier en mode "a" (ajout) s'il existe, sinon création et ouverture en mode "w" (écriture)
    with open(chemin_journalisation, "a" if fichier_existe else "w", encoding="utf-8") as journal_file:
        journal_file.write(message + "\n")

# fichier_siren = "siren.txt"
dossier_siren = "dossier_siren"

# Chamar a função para ler os SIRENs
# siren_list, nb_siren = lecture_liste_siren(fichier_siren)
siren_list, nb_siren = lecture_liste_siren(df, 'siren')
print(f"{nb_siren} SIRENs encontrados no arquivo.")

# Para cada SIREN, tentar baixar os documentos
for siren in siren_list:
    try:
        telecharge_documents(siren, token, dossier_siren)
    except Exception as e:
        print(f"Erro ao processar o SIREN {siren}: {str(e)}")

