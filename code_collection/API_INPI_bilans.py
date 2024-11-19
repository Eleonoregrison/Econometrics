# TÉLÉCHARGER LES BILANS PAR SIREN
# Pour utiliser le code, il faut d'avoir le fichier etablissements_ETI_GE.csv et un dossier nommé dossier_siren dans le répertoire

# Bibliothèque utilisée
import pandas as pd
import requests
import json
import os
import sys

# Compte
username = "davi-lucena.souza@etu.minesparis.psl.eu"
password = "020173ivadJanice@1"

# URL de L'API
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

# Fonction pour vérifier si le fichier existe déjà dans le répertoire afin de ne pas télécharger à nouveau
def fichier_existe(chemin_fichier):
    return os.path.exists(chemin_fichier)

# Lecture des SIREN à interroger à partir d'une colonne d'un DataFrame
df = pd.read_csv('etablissements_ETI_GE.csv', dtype={'colonne_siren': str}, low_memory=False)
def lecture_liste_siren(dataframe, colonne_siren):
    # Garante que os valores sejam strings, remove nulos e preenche com zeros à esquerda
    liste_siren = dataframe[colonne_siren].dropna().astype(str).str.zfill(9).tolist()
    nb_siren = len(liste_siren)
    return liste_siren, nb_siren

# Pour télécharger uniquement une année, indiquez l'année souhaitée dans la variable
anne = "2023"


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
                    
                        if document_date_cloture and document_date_cloture.startswith(anne):
                            nom_fichier = f"{siren}_{document_date_cloture}.pdf"
                            telecharge_document(document_type, document_id, nom_fichier, siren, token, dossier_siren)
                            print(f"{document_date_cloture}")
                        else:
                            print(f"{document_date_cloture}")
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
    except Exception as e:
        message=f"Une exception s'est produite lors du téléchargement du document : {str(e)}"
        message_complet=message_complet + message
        print(message)

# fichier_siren = "siren.txt"
dossier_siren = "dossier_siren"

# Chamar a função para ler os SIRENs
# siren_list, nb_siren = lecture_liste_siren(fichier_siren)
siren_list, nb_siren = lecture_liste_siren(df, 'siren')
print(f"{nb_siren} SIRENs encontrados no arquivo.")

# Définit le SIREN à partir duquel vous souhaitez commencer l'analyse
siren_debut = "130012636"

# Pour chaque SIREN, essayer de télécharger les documents à partir de siren_debut
traitement_commence = False  # Variable de contrôle pour commencer le traitement

for siren in siren_list:
    # Vérifie si le SIREN à partir duquel vous souhaitez commencer a été trouvé
    if not traitement_commence:
        if siren == siren_debut:
            traitement_commence = True  # Commence le traitement
        else:
            continue  # Ignore les SIRENs jusqu'à trouver le bon

    # Maintenant que le SIREN a été trouvé, continue le traitement
    try:
        telecharge_documents(siren, token, dossier_siren)
        sys.exit(1)  # Arrête immédiatement l'exécution du programme
    except Exception as e:
        print(f"Erreur lors du traitement du SIREN {siren} : {str(e)}")
