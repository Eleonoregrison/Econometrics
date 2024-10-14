# %%
import scipy.special as sc
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.special as sc
import pyarrow as pa
# %% [markdown]
# **Base de donnée sirene donnant la catégorie des entreprises**

# %%
df_ETI_GE = pd.read_csv('etablissements_ETI_GE.csv', low_memory=False)
nombre_entreprises =df_ETI_GE['siren'].nunique()
print(nombre_entreprises)
df_ETI_GE

# %% [markdown]
# Voila le data frame obtenu avec la base sirene permettant de classer les SIREN en GE et ETI. Il compte 130361 établissements siège.

# %%
# Obtenir et afficher la liste des colonnes
colonnes = df_ETI_GE.columns.tolist()
colonnes

# %% [markdown]
# **Base de donnée donnant les entreprises qui ont le CIR et les années d'agrément**\
# Données de 2009 à 2031

# %%
df_CI = pd.read_csv ('CSV_CIR_CII.csv', sep = ';')

# Remplacer les valeurs non valides par NaN
df_CI['Numéro SIREN'] = pd.to_numeric(df_CI['Numéro SIREN'], errors='coerce')

# Vérifier les valeurs nulles après la conversion
print(df_CI['Numéro SIREN'].isnull().sum())  # Pour voir combien de NaN ont été générés

# Option 1 : Supprimer les lignes avec des NaN dans 'Numero SIREN'
df_CI['Numéro SIREN'] = df_CI['Numéro SIREN'].fillna(0).astype(int)

df_CI.rename(columns={'Numéro SIREN': 'siren'}, inplace=True)

print (df_CI.columns)
df_CI['siren']
# %%
# Garder seulement les entreprises qui ont le CIR
df_CIR = df_CI[df_CI['Dispositif'] == 'CIR']

# Afficher les premières lignes pour vérifier le résultat
print (len(df_CIR))
df_CIR.head()

# %%
# Compter le nombre d'entreprises par pays
counts_par_pays = df_CIR['Pays'].value_counts()*100/len(df_CIR)

# Créer un histogramme
plt.figure(figsize=(10, 6))
counts_par_pays[1:].plot(kind='bar', color='skyblue')
plt.title('Pourcentage d\'agréments par pays')
plt.xlabel('Pays')
plt.ylabel('Pourcentage d\'agréments')
plt.xticks(rotation=45)  # Faire pivoter les étiquettes des axes x pour une meilleure lisibilité
plt.grid(axis='y')

# Afficher le graphique
plt.tight_layout()
plt.show()


# %%
df_CIR['Année d\'agrément'][df_CIR['Pays']!='France'].unique()

# %%
type(df_CIR['Année d\'agrément'][0])

# %%
# Créer une liste des années de 2009 à 2031
df_CIR["Année d'agrément"] = df_CIR["Année d'agrément"].apply(lambda x: list(map(int, x.split(','))))

# Créer une liste des années de 2009 à 2031
annees = list(range(2009, 2032))

# Créer un DataFrame pour chaque année
for annee in annees:
    df_CIR[annee] = df_CIR["Année d'agrément"].apply(lambda x: 1 if annee in x else 0)

# Afficher le DataFrame modifié
df_CIR

# %% [markdown]
# df_CIR est le dataframe qui contient les entreprises (de toute catégorie) recevant le CIR et donnant les années d'agrément. Pour chaque année, une colonne dit quelles entreprises ont l'agrément.

# %%

# Calculer le nombre d'agréments par année
nombre_agrements = df_CIR[annees].sum()

# Tracer le graphique
plt.figure(figsize=(12, 6))
nombre_agrements.plot(kind='bar', color='skyblue')
plt.title('Nombre d\'agréments par année')
plt.xlabel('Année')
plt.ylabel('Nombre d\'agréments')
plt.xticks(rotation=45)  # Rotation des étiquettes de l'axe des x
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()  # Ajuster le layout
plt.show()

# %%
# Calculer le nombre d'agréments par année
nombre_agrements_etrangers = df_CIR[df_CIR['Pays']!='France'][annees].sum()

# Tracer le graphique
plt.figure(figsize=(12, 6))
nombre_agrements_etrangers.plot(kind='bar', color='skyblue')
plt.title('Nombre d\'agréments par année pour les entreprises étrangères')
plt.xlabel('Année')
plt.ylabel('Nombre d\'agréments')
plt.xticks(rotation=45)  # Rotation des étiquettes de l'axe des x
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()  # Ajuster le layout
plt.show()

# %%
# Calculer le nombre d'agréments par année
nombre_agrements_all = df_CIR[df_CIR['Pays']=='Allemagne'][annees].sum()

# Tracer le graphique
plt.figure(figsize=(12, 6))
nombre_agrements_all.plot(kind='bar', color='skyblue')
plt.title('Nombre d\'agréments par année pour les entreprises allemandes')
plt.xlabel('Année')
plt.ylabel('Nombre d\'agréments')
plt.xticks(rotation=45)  # Rotation des étiquettes de l'axe des x
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()  # Ajuster le layout
plt.show()

# %%
# Calculer le nombre d'agréments par année
nombre_agrements_etrangers = df_CIR[df_CIR['Pays']=='France'][annees].sum()

# Tracer le graphique
plt.figure(figsize=(12, 6))
nombre_agrements_etrangers.plot(kind='bar', color='skyblue')
plt.title('Nombre d\'agréments par année pour les entreprises françaises')
plt.xlabel('Année')
plt.ylabel('Nombre d\'agréments')
plt.xticks(rotation=45)  # Rotation des étiquettes de l'axe des x
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()  # Ajuster le layout
plt.show()

# %%
fig, axs = plt.subplots(2, 2, figsize=(12, 8))  # 2x2 sous-graphiques
axs = axs.flatten()  # Aplatir la matrice pour faciliter l'itération

# Calculer le nombre d'agréments par année
nombre_agrements = df_CIR[annees].sum()
nombre_agrements_français = df_CIR[df_CIR['Pays']=='France'][annees].sum()
nombre_agrements_etrangers = df_CIR[df_CIR['Pays']!='France'][annees].sum()
nombre_agrements_all = df_CIR[df_CIR['Pays']=='Allemagne'][annees].sum()

axs[0].bar(annees, nombre_agrements, color='skyblue')
axs[0].set_title(f'Nombre d\'agréments par année')
axs[0].set_ylabel('Nombre d\'agréments')


axs[1].bar(annees, nombre_agrements_français, color='skyblue')
axs[1].set_title(f'Nombre d\'agréments par années des entreprises françaises')
axs[1].set_ylabel('Nombre d\'agréments')

axs[2].bar(annees, nombre_agrements_etrangers, color='skyblue')
axs[2].set_title(f'Nombre d\'agréments par années des entreprises étrangères')
axs[2].set_ylabel('Nombre d\'agréments')

axs[3].bar(annees, nombre_agrements_all, color='skyblue')
axs[3].set_title(f'Nombre d\'agréments par années des entreprises allemandes')
axs[3].set_ylabel('Nombre d\'agréments')

plt.show()

# %% [markdown]
# Pour tous les pays il semble y avoir un pique en 2O22. Comment l'expliquer ? 

# %%

# Calculer le nombre d'entreprises par secteur (seulement les secteurs qui représentent plus de 200 agréments)
entreprises_par_secteur = df_CIR['Activité'].value_counts()
entreprises_par_secteur = entreprises_par_secteur[entreprises_par_secteur >= 200]
# Créer l'histogramme
plt.figure(figsize=(10, 6))
plt.bar(entreprises_par_secteur.index, entreprises_par_secteur.values, color='skyblue')

# Ajouter des labels
plt.xlabel('Secteur')
plt.ylabel('Nombre d\'agréments')
plt.title('Répartition des agréments par secteur pour toute catégorie d\'entreprises')
plt.xticks(rotation=45)
plt.grid(axis='y')
plt.xticks(rotation=45, ha='right')
# Afficher le graphique
plt.tight_layout()  # Pour ajuster le layout
plt.show()

# %% [markdown]
# On voit donc que le secteur de l'informatique est celui qui bénéficie le plus du CIR.

# %%
df_CIR_completed = pd.merge(df_CIR, df_ETI_GE[['siren', 'categorieEntreprise']], on='siren', how='left')
# Remplacer les valeurs manquantes dans df1['categorie'] avec celles de df2['categorie']
df_CIR_completed['Base SIRENE : Catégorie de l\'établissement siège'] = df_CIR_completed['Base SIRENE : Catégorie de l\'établissement siège'].combine_first(df_CIR_completed['categorieEntreprise'])

# Supprimer la colonne supplémentaire qui est venue du second DataFrame après la fusion
df_CIR_completed = df_CIR_completed.drop(columns=['categorieEntreprise'])

# Afficher les premières lignes pour vérifier
df_CIR_completed['Base SIRENE : Catégorie de l\'établissement siège']

valeurs_uniques = df_CIR_completed['Base SIRENE : Catégorie de l\'établissement siège'].value_counts()
print (valeurs_uniques)

# %% [markdown]
# On refait rapidement les mêmes graphiques pour GE et ETI

# %% [markdown]
# Exemple d'entreprises allemande > pas de numéro siren \
# Les coordonnées donnent dans le pays d'origine

# %%
print(df_CIR_completed.loc[
    (df_CIR_completed['Pays'] == 'Allemagne') & (df_CIR_completed ['Nom de l\'entreprise']=='APERTO GMBH')])


# %%
fig, axs = plt.subplots(1, 2, figsize=(12, 8))  # 2x2 sous-graphiques
axs = axs.flatten()  # Aplatir la matrice pour faciliter l'itération

# Calculer le nombre d'agréments par année

nombre_agrements_ETI = df_CIR_completed.loc[
    (df_CIR_completed['Pays'] == 'France') & 
    (df_CIR_completed['Base SIRENE : Catégorie de l\'établissement siège'] == 'ETI'), 
    annees
].sum()
nombre_agrements_GE = df_CIR_completed.loc[
    (df_CIR_completed['Pays'] == 'France') & 
    (df_CIR_completed['Base SIRENE : Catégorie de l\'établissement siège'] == 'GE'), 
    annees
].sum()


# Création des sous-histogrammes
axs[0].bar(annees, nombre_agrements_ETI, color='skyblue')
axs[0].set_title(f'Nombre d\'agréments par année des entreprises françaises pour les ETI')
axs[0].set_ylabel('Nombre d\'agréments')

axs[1].bar(annees, nombre_agrements_GE, color='skyblue')
axs[1].set_title(f'Nombre d\'agréments par années des entreprises françaises pour les GE')
axs[1].set_ylabel('Nombre d\'agréments')
max_value = max(nombre_agrements_ETI.max(), nombre_agrements_GE.max())
for ax in axs:
    ax.set_ylim(0, max_value+10)
plt.tight_layout()
plt.show()

# %% [markdown]
# Parfois, une entreprise a eu plusieurs agréments et donc plusieurs lignes ont le même numéro siren. Je veux regrouper les agréments en ajoutant les années sur une même ligne. 

# %%
# Calculer le nombre d'entreprises par secteur (seulement les secteurs qui représentent plus de 200 agréments)
entreprises_par_secteur = df_CIR_completed.loc[df_CIR_completed['Base SIRENE : Catégorie de l\'établissement siège'] == 'ETI' ,'Activité'].value_counts()
entreprises_par_secteur = entreprises_par_secteur[entreprises_par_secteur >= 30]
# Créer l'histogramme
plt.figure(figsize=(10, 6))
plt.bar(entreprises_par_secteur.index, entreprises_par_secteur.values, color='skyblue')

# Ajouter des labels
plt.xlabel('Secteur')
plt.ylabel('Nombre d\'agréments')
plt.title('Répartition des agréments par secteur pour les ETI')
plt.xticks(rotation=45)
plt.grid(axis='y')
plt.xticks(rotation=45, ha='right')
# Afficher le graphique
plt.tight_layout()  # Pour ajuster le layout
plt.show()

# %%
# Calculer le nombre d'entreprises par secteur (seulement les secteurs qui représentent plus de 200 agréments)
entreprises_par_secteur = df_CIR_completed.loc[df_CIR_completed['Base SIRENE : Catégorie de l\'établissement siège'] == 'GE' ,'Activité'].value_counts()
entreprises_par_secteur = entreprises_par_secteur[entreprises_par_secteur >= 10]
# Créer l'histogramme
plt.figure(figsize=(10, 6))
plt.bar(entreprises_par_secteur.index, entreprises_par_secteur.values, color='skyblue')

# Ajouter des labels
plt.xlabel('Secteur')
plt.ylabel('Nombre d\'agréments')
plt.title('Répartition des agréments par secteur pour les GE')
plt.xticks(rotation=45)
plt.grid(axis='y')
plt.xticks(rotation=45, ha='right')
# Afficher le graphique
plt.tight_layout()  # Pour ajuster le layout
plt.show()

# %%
import folium
from folium.plugins import MarkerCluster

# Séparer la colonne 'Géolocalisation' en deux colonnes : 'latitude' et 'longitude'
df_CIR_completed[['latitude', 'longitude']] = df_CIR_completed['Géolocalisation'].str.split(',', expand=True)

# Convertir les colonnes latitude et longitude en float
df_CIR_completed['latitude'] = df_CIR_completed['latitude'].astype(float)
df_CIR_completed['longitude'] = df_CIR_completed['longitude'].astype(float)


# Créer la carte
carte = folium.Map(location=[46.603354, 1.888334], zoom_start=6)

# Ajouter des clusters de points
marker_cluster = MarkerCluster().add_to(carte)

# Ajouter des marqueurs dans le cluster
for index, row in df_CIR_completed.iterrows():
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=row['siren']
    ).add_to(marker_cluster)

# Sauvegarder ou afficher la carte
carte.save("carte_entreprises_cluster.html")

# %%
df_allemandes = df_CIR_completed[df_CIR_completed['Pays'] == 'Allemagne']
df_allemandes


# %% [markdown]
# Toutes les entreprises etrangères ont une seule localisation par pays.

# %%
# Fonction pour combiner les informations d'une colonne, séparées par une nouvelle ligne et un point-virgule
def combiner_informations_nouvelle_ligne(colonne):
    uniques = colonne.unique()  # Obtenir les valeurs uniques dans la colonne
    if len(uniques) > 1:  # Si plusieurs valeurs uniques existent, on les combine
        return '; '.join(map(str, uniques))  # Séparer par une nouvelle ligne et un point-virgule
    else:
        return str(uniques[0])  # Si toutes les valeurs sont identiques, on garde la première

# Regrouper les lignes par 'siren' et appliquer des fonctions d'agrégation sur les autres colonnes
df_grouped = df_CIR.groupby('siren').agg({
    'Dispositif': combiner_informations_nouvelle_ligne,  # Garde la première valeur rencontrée pour chaque siren
    'Type de structure': combiner_informations_nouvelle_ligne,
    "Année d'agrément": combiner_informations_nouvelle_ligne,  # Garde l'année d'agrément la plus récente
    'Activité': combiner_informations_nouvelle_ligne,
    'Localisation': combiner_informations_nouvelle_ligne,
    "Début d'agrément": combiner_informations_nouvelle_ligne,  # Prend la première année d'agrément
    "Fin d'agrément": combiner_informations_nouvelle_ligne,    # Prend la dernière année d'agrément
    "Nom de l'entreprise": combiner_informations_nouvelle_ligne,
    'Sigle': combiner_informations_nouvelle_ligne,
    'Code postal' : combiner_informations_nouvelle_ligne,
    'Ville' : combiner_informations_nouvelle_ligne,
    'Commune' : combiner_informations_nouvelle_ligne, 
    'Unité urbaine': combiner_informations_nouvelle_ligne,
    'Département': combiner_informations_nouvelle_ligne,
    'Académie': combiner_informations_nouvelle_ligne,
    'Région': combiner_informations_nouvelle_ligne,
    'Pays': combiner_informations_nouvelle_ligne,
    'Code commune (France)': combiner_informations_nouvelle_ligne,
    'Code de l\'unité urbaine (France)':combiner_informations_nouvelle_ligne,
    'Code du département (France)': combiner_informations_nouvelle_ligne,
    'Code de l\'académie (France)': combiner_informations_nouvelle_ligne,
    'Code de la région (France)':combiner_informations_nouvelle_ligne, 
    'Géolocalisation' : combiner_informations_nouvelle_ligne
    # Ajoute d'autres colonnes et leurs méthodes d'agrégation si nécessaire
})
df_grouped.reset_index(inplace=True)
# Afficher les premières lignes du DataFrame regroupé
df_grouped

# %%
# Compter le nombre d'entreprises par pays
nombre_entreprises_par_pays = df_grouped['Pays'].value_counts()

# Afficher le résultat
print(nombre_entreprises_par_pays)

# %% [markdown]
# **Premier Dataframe auquel on ajoute les années d'agrément au CIR des entreprises**

# %%
df_merged = pd.merge(df_ETI_GE, df_grouped[['siren', 'Année d\'agrément']], on='siren', how='left')
df_merged.iloc[1000:1051]

# %%
# Compter le nombre de NaN dans une colonne spécifique, par exemple 'colonne'
nb_nan = df_merged['Année d\'agrément'].isna().sum()

# Afficher le résultat
print(nb_nan)

# %%
print ('Le nombre d\'unité légale siège reçevant le CIR est :', nombre_entreprises - nb_nan)

# %%
# Lire le fichier TSV
df = pd.read_csv('estat_bd_size.tsv', sep='\t')
df

# %%

# %%
