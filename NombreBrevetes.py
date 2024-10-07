#Tapez le nom de l'entreprise et vous obtiendrez le nombre de brevets trouvés

import time
import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
import re

# +
# GooglePatents
# Fonction pour rechercher le nombre de brevets pour une entreprise donnée
def chercher_nombre_de_brevets_Google(entreprise):
    # Initialiser le ChromeDriver
    SERVICE_PATH = "C:\\Users\\davil\\Downloads\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe"
    service = Service(SERVICE_PATH)
    driver = webdriver.Chrome(service=service)

    # Formater le nom de l'entreprise pour l'URL
    entreprise_formatée = entreprise.replace(" ", "+")

    # Ouvrir la page Google Patents pour l'entreprise donnée en français
    url = f"https://patents.google.com/?assignee={entreprise_formatée}&oq={entreprise_formatée}&hl=fr"
    driver.get(url)

    # Attendre que la page se charge complètement
    time.sleep(2)

    # Analyser le HTML de la page avec BeautifulSoup
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Trouver tous les éléments <span> avec la classe "style-scope search-results"
    result_span = soup.find_all("span", class_="style-scope search-results")

    # Parcourir les éléments pour trouver le nombre de brevets (qui est un chiffre)
    nombre_de_brevets = None
    for span in result_span:
        if span.text.isdigit():  # Vérifier si le texte est un chiffre
            nombre_de_brevets = span.text
            print(f"Nombre de brevets pour {entreprise}: {span.text}")
            break  # Arrêter la boucle une fois que le nombre est trouvé

    # Fermer le navigateur
    driver.quit()

    # Créer un DataFrame avec le nom de l'entreprise et le nombre de brevets
    if nombre_de_brevets:
        df = pd.DataFrame({
            'Entreprise': [entreprise],
            'Nombre de brevets': [nombre_de_brevets]
        })
        return df
    else:
        print(f"Impossible de trouver le nombre de brevets pour {entreprise}.")
        return None

# +
# INPI
# Fonction pour rechercher le nombre de brevets pour une entreprise donnée
def chercher_nombre_de_brevets_INPI(entreprise):
    # Initialiser le ChromeDriver
    SERVICE_PATH = "C:\\Users\\davil\\Downloads\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe"
    service = Service(SERVICE_PATH)
    driver = webdriver.Chrome(service=service)

    # Formater le nom de l'entreprise pour l'URL
    entreprise_formatée = entreprise.replace(" ", "%20")

    # Ouvrir la page INPI pour l'entreprise donnée
    url = f"https://data.inpi.fr/search?advancedSearch=%257B%257D&filter=%257B%257D&nbResultsPerPage=20&order=asc&page=1&q={entreprise_formatée}&sort=relevance&type=patents"
    driver.get(url)

    # Attendre que la page se charge complètement
    time.sleep(3)

    # Analyser le HTML de la page avec BeautifulSoup
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Chercher l'élément qui contient le texte "Brevets (XX)"
    brevet_section = soup.find("span", string=re.compile(r"Brevets \(\d+\)"))  # Remplace 'text' par 'string'
    
    # Vérifier si le nombre de brevets est trouvé
    nombre_de_brevets = None
    if brevet_section:
        # Extraire le nombre de brevets entre parenthèses
        match = re.search(r"\((\d+)\)", brevet_section.text)
        if match:
            nombre_de_brevets = match.group(1)
            print(f"Nombre de brevets pour {entreprise}: {nombre_de_brevets}")
    else:
        print(f"Impossible de trouver le nombre de brevets pour {entreprise}.")

    # Fermer le navigateur
    driver.quit()

    # Créer un DataFrame avec le nom de l'entreprise et le nombre de brevets
    if nombre_de_brevets:
        df = pd.DataFrame({
            'Entreprise': [entreprise],
            'Nombre de brevets': [nombre_de_brevets]
        })
        return df
    else:
        return None

# Demander INPI
# Demander à l'utilisateur d'entrer le nom de l'entreprise
nom_entreprise = input("Entrez le nom de l'entreprise : ")

# Appel de la fonction pour rechercher les brevets de l'entreprise donnée (ex: ALFA LAVAL VICARB)
df_brevets = chercher_nombre_de_brevets_INPI(nom_entreprise)

df_brevets
