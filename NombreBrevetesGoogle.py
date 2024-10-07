#Tapez le nom de l'entreprise et vous obtiendrez le nombre de brevets trouvés sur GooglePatents.

import time
import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service

# Fonction pour rechercher le nombre de brevets pour une entreprise donnée
def chercher_nombre_de_brevets(entreprise):
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

# Demander à l'utilisateur d'entrer le nom de l'entreprise
nom_entreprise = input("Entrez le nom de l'entreprise : ")

# Appel de la fonction pour rechercher les brevets de l'entreprise donnée
df_brevets = chercher_nombre_de_brevets(nom_entreprise)

df_brevets
