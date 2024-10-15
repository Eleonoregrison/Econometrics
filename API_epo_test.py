import requests
import urllib.parse
import base64
import json
import xml.etree.ElementTree as ET


def ops_authentification():
    # Convert client credentials to an access token, in order to consume resource from the OPS service
    # Client credentials
    consumer_key = "AhMvO8Kv17x0GszHaUnS9QGj8GVR92wU1ojTNEsFITirRLxL"
    consumer_secret_key = "fgrznp1As3srmkG7k2TxAcAZBUXwp6F7MALDcRPy3pMNpldxADsJnH648NqytpUB"

    ## Step 1 :  Client converts Consumer key and Consumer secret to Base64Encode(Consumer key:Consumer secret)
    client_credentials = consumer_key + ":" + consumer_secret_key
    client_credentials = client_credentials.encode("UTF-8")  # convert string to bytes
    client_credentials = base64.b64encode(client_credentials)  # encode bytes
    client_credentials = client_credentials.decode("UTF-8")  # convert bytes to string

    ## Step 2: Client requests an access token using Basic Authentication
    ## If credentials are valid, OPS responds with a valid access token (valid for 20 min)
    print("OPS Authentification...")
    url = "https://ops.epo.org/3.2/auth/accesstoken"
    headers = {
        "Authorization": "Basic " + client_credentials,
        "Content-Type": "application/x-www-form-urlencoded",
    }
    payload = {"grant_type": "client_credentials"}
    response = requests.post(url, data=payload, headers=headers)
    if response.status_code != 200:
        print(f"Error: {response.status_code=}")
        print(response.text)
        exit()
    response = json.loads(response.text)  # convert JSON to Python dictionary
    access_token = response["access_token"]  # extract access token from response
    print("Succeeded")
    return access_token
ops_authentification()


# +
def get_patents(company_name, access_token):
    # Encoder le nom de l'entreprise pour l'URL
    encoded_company_name = urllib.parse.quote(company_name)

    # URL de recherche avec le nom de l'entreprise encodé
    url = f"https://ops.epo.org/3.2/rest-services/published-data/search/biblio?q=applicant:\"{encoded_company_name}\""
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    
    # Envoyer la requête
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erreur pour {company_name}: {response.status_code}")
        return None

# Exemple d'utilisation
consumer_key = "Votre_Cle"  # Remplacez par votre clé API
consumer_secret = "Votre_Secret"  # Remplacez par votre secret API

# Authentification
token = ops_authentification()

# Liste des entreprises
companies = ["ALFA LAVAL VICARB"]  # Remplacez par vos entreprises

# Dictionnaire pour stocker les brevets par entreprise
patents_dict = {}

# Recherche des brevets pour chaque entreprise
for company in companies:
    print(f"Recherche des brevets pour {company}...")
    patents = get_patents(company, token)
    
    if patents:
        # Extraction des brevets
        search_results = patents.get("ops:world-patent-data", {}).get("ops:biblio-search", {}).get("ops:search-result", {}).get("exchange-documents", [])
        
        patents_list = []  # Liste pour stocker les brevets de l'entreprise
        
        if search_results:
            for doc in search_results:
                document = doc.get("exchange-document", {})
                family_id = document.get("@family-id", "N/A")
                country = document.get("@country", "N/A")
                doc_number = document.get("@doc-number", "N/A")
                publication_ref = document.get("bibliographic-data", {}).get("publication-reference", {}).get("document-id", [])

                # Récupérer la date de publication
                publication_date = None
                for ref in publication_ref:
                    if ref.get("date"):
                        publication_date = ref["date"]["$"]

                patents_list.append({
                    "family_id": family_id,
                    "country": country,
                    "doc_number": doc_number,
                    "publication_date": publication_date,
                })
            
            # Ajouter les brevets trouvés à notre dictionnaire
            patents_dict[company] = patents_list
        else:
            print(f"Aucun résultat trouvé pour {company}.")
    else:
        print(f"Erreur lors de la récupération des brevets pour {company}.")

# Affichage des résultats
for company, patents in patents_dict.items():
    print(f"\nBrevets pour {company}:")
    for patent in patents:
        print(f" - Famille ID: {patent['family_id']}, Pays: {patent['country']}, Numéro de Document: {patent['doc_number']}, Date de Publication: {patent['publication_date']}")
# -

# On remarque plusieurs problème dans cette première tentative : 
# - Nous avons seulement récupéré les brevets publiés en 2024 ;
# - Lorsque je cherche une entreprise de ma base de donnée qui a publié des brevets selon INPI, on obtient une erreur 404.
