import scipy.special as sc
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.special as sc


# +
# Fonction qui modélise la distribution de la loi de Yule avec la fonction bêta
def yule_distribution(k, rho):
    # Utilisation de la fonction bêta pour la loi de Yule
    return rho*sc.beta(k, rho + 1)

# Valeurs de rho à tester
rho_values = [0.25, 0.5, 1, 2, 4]

# Valeurs de k (nombre d'occurrences, entier positif)
k_values = np.arange(1, 100)

# Traçage de la distribution pour chaque valeur de rho
plt.figure(figsize=(10, 6))

for rho in rho_values:
    # Calcul de la fonction pour chaque k pour un certain rho
    yule_values = yule_distribution(k_values, rho)
    
    # Tracer la courbe
    plt.plot(k_values, yule_values, label=f'rho = {rho}')

# Configurer le graphique
plt.title('Distribution de la loi de Yule modélisée avec la fonction Bêta')
plt.xlabel('k (Nombre d\'occurrences)')
plt.ylabel('f(k)')
plt.xscale('log')  # Echelle linéaire sur l'axe des abscisses
plt.yscale('log')  # Echelle logarithmique sur l'axe des ordonnées
plt.legend(title="Valeurs de rho")
plt.grid(True)

# Afficher le graphique
plt.show()

# +
# Générer des échantillons aléatoires suivant la distribution de Yule
rho1=0.1
def generate_yule_samples(rho1, size=1000):
    # Nombre d'occurrences possibles (k)
    k_values = np.arange(1, 10000)
    
    # Calculer la distribution de probabilités
    probabilities = yule_distribution(k_values, rho1)
    
    # Normaliser les probabilités pour qu'elles forment une distribution de probabilité valide
    probabilities /= np.sum(probabilities)
    
    # Générer des échantillons selon cette distribution
    samples = np.random.choice(k_values, size=size, p=probabilities)
    return samples

# Générer des échantillons selon la loi de Yule pour un certain rho
samples = generate_yule_samples(rho1, size=10000)

# Afficher un histogramme des échantillons
plt.figure(figsize=(10, 6))
plt.hist(samples, bins=50, density=False, alpha=0.6, color='g')
plt.title(f'Échantillons générés selon la loi de Yule (rho = {rho1})')
plt.xlabel('Valeur de k')
plt.ylabel('Densité')
plt.grid(True)
plt.show()

# +
df = pd.DataFrame(samples, columns=['Year_0'])

# Distribution de croissance des entreprises
def laplace_distribution (g,a): 
    return np.exp(-np.abs(g)/a)/(2*a)

# # +
a_values = [1,2,4]
g_values = np.linspace(-10, 10, 10000)

# Traçage de la distribution pour chaque valeur de a
plt.figure(figsize=(10, 6))

for a in a_values:
    # Calculer la distribution de Laplace pour chaque g
    laplace_values = laplace_distribution(g_values, a)
    
    # Tracer la courbe
    plt.plot(g_values, laplace_values, label=f'a = {a}')

# Configurer le graphique
plt.title('Distribution de Laplace pour différents a')
plt.xlabel('g')
plt.ylabel('f(g; a)')
plt.legend(title="Valeurs de a")
plt.grid(True)

# Afficher le graphique
plt.show()


# +
# Générer des échantillons aléatoires selon la distribution de Laplace
def generate_laplace_samples(a, size=10000):
    # Générer des nombres aléatoires uniformes
    u = np.random.uniform(0, 1, size)
    
    # Utiliser la méthode de transformation inverse pour échantillonner
    samples = np.where(u < 0.5,
                       a * np.log(2 * u),        # pour g < 0
                       -a * np.log(2 * (1 - u))) # pour g >= 0
    return samples

# Valeur de a à tester
a = 6 # Tu peux changer cette valeur pour tester d'autres cas
# -


years = 10
for year in range(1, years + 1):
    # Vérifie que la taille de df est correcte
    print(f"Taille du DataFrame avant génération : {len(df)}")

    # Générer la croissance pour l'année suivante
    df[f'Growth_{year}'] = generate_laplace_samples(a, len(df))  # Assurez-vous que cela correspond

    # Calculer l'année suivante
    df[f'Year_{year}'] = (100 + df[f'Growth_{year}']) / 100 * df[f'Year_{year-1}']
    
    # Arrondir les valeurs à l'entier le plus proche
    df[f'Year_{year}'] = df[f'Year_{year}'].round()
    
    # Remplacer les valeurs inférieures à 1 par 0
    df.loc[df[f'Year_{year}'] < 1, f'Year_{year}'] = 0
    
    # Trouver les indices où un zéro est apparu pour cette année
    zeros_indices = df[df[f'Year_{year}'] == 0].index
    
    # Générer des échantillons de la distribution de Yule pour ces indices
    if len(zeros_indices) > 0:
        yule_samples = generate_yule_samples(rho1, len(zeros_indices))
        
        # Créer un nouveau DataFrame pour les nouvelles lignes
        new_rows = df.loc[zeros_indices].copy()
        
        # Remplacer les valeurs dans le DataFrame temporaire par les valeurs de la distribution de Yule
        for i in range(year): 
            new_rows[f'Year_{i}'] = 0
        new_rows[f'Year_{year}'] = yule_samples
        
        # Ajouter les nouvelles lignes au DataFrame d'origine
        df = pd.concat([df, new_rows], ignore_index=True)

    print(f"Taille du DataFrame après génération : {len(df)}")


# +
"""# Répéter le processus de croissance sur 10 ans
years = 10
for year in range(1, years + 1):
    # Générer la croissance pour l'année suivante
    df[f'Growth_{year}'] = generate_laplace_samples(a)
    
    # Calculer l'année suivante
    df[f'Year_{year}'] = (100 +df[f'Growth_{year}'] )/100*  df[f'Year_{year-1}']
    # Arrondir les valeurs à l'entier le plus proche
    df[f'Year_{year}'] = df[f'Year_{year}'].round()
    
    # Remplacer les valeurs inférieures à 1 par 0
    df.loc[df[f'Year_{year}'] < 1, f'Year_{year}'] = 0
    
    # Remplacer les zéros par des valeurs tirées de la distribution de Yule
    zeros_indices = df[df[f'Year_{year}'] == 0].index
    yule_samples = generate_yule_samples(rho1, len(zeros_indices))
    df.loc[zeros_indices, f'Year_{year}'] = yule_samples"""
        
# Tracer une grille de 11 sous-graphes
fig, axs = plt.subplots(7, 3, figsize=(30, 20))  # 7 lignes et 3 colonnes
axs = axs.flatten()

# Tracer chaque année dans un sous-graphe
for year in range(years + 1):
    axs[year].hist(df[f'Year_{year}'], bins=50, alpha=0.6, color='g')
    axs[year].set_title(f'Distribution de Year pour l\'année { year}')
    axs[year].set_xlabel('Year Value')
    axs[year].set_ylabel('Frequency')
    axs[year].grid(True)
    
    # Afficher le nombre d'échantillons
    n_samples = df[f'Year_{year}'].count()  # Compter le nombre d'échantillons
    axs[year].text(0.5, 0.9, f'N={n_samples}', transform=axs[year].transAxes,
                   fontsize=10, ha='center', bbox=dict(facecolor='white', alpha=0.5))

# Supprimer les sous-graphes vides (il y a 12 sous-graphes au total)
for j in range(years + 1, 21):
    fig.delaxes(axs[j])

# Ajuster l'espacement entre les sous-graphes
plt.tight_layout()

# Afficher le graphique
plt.show()
# -

df


# +
# Tracer une grille de 11 sous-graphes
fig, axs = plt.subplots(3, 4, figsize=(15, 20))  # 7 lignes et 3 colonnes
axs = axs.flatten() 

for year in range(1, years):
    axs[year].hist(df[f'Growth_{year}'], bins=50, density=True, alpha=0.6, color='g')
    axs[year].set_title(f'Échantillons générés selon la distribution de Laplace (a = {a}) de lannée {year}')
    axs[year].set_xlabel('taux de croissance')
    axs[year].set_ylabel('Densité')
    axs[year].grid(True)
    g_values = np.linspace(-10, 10, 1000)
    laplace_values = laplace_distribution(g_values, a)
    axs[year].plot(g_values, laplace_values, color='r', lw=2, label=f'Distribution de Laplace (a={a})')
    

# Supprimer les sous-graphes vides (il y a 12 sous-graphes au total)
for j in range(years + 1, 12):
    fig.delaxes(axs[j])

# Ajuster l'espacement entre les sous-graphes
plt.tight_layout()

plt.show()


# +
columns =[]
growths =[]
for year in range(years):
    columns.append(f'Year_{year}')
    if year!=0:
        growths.append(f'Growth_{year}')
print(columns)
print(growths)

df_fin10 = df.tail(10)[columns]

# Définir les années
#years = df.columns[1:]  # Ignorer la colonne 'Entreprise'

# Tracer les effectifs des 10 premières entreprises
plt.figure(figsize=(12, 6))

for index, row in df_fin10.iterrows():
    plt.plot(columns, row, marker='o')

plt.title('Effectifs des 10 dernières Entreprises par Année')
plt.xlabel('Année')
plt.ylabel('Effectif')
plt.xticks(rotation=45)  # Rotation des labels d'axes x pour une meilleure lisibilité
plt.grid(True)
plt.legend(title='Entreprises', bbox_to_anchor=(1.05, 1), loc='upper left')  # Légende à droite
plt.tight_layout()  # Ajuste l'espace pour éviter le chevauchement
plt.show()

# +
donnes= df.drop(['Growth_1','Growth_2','Growth_3','Growth_4','Growth_5','Growth_6','Growth_7','Growth_8','Growth_9','Growth_10'], axis=1)

entreprise_interet=[]
date_franchissement= []
data= {}
for i in range(-9,11,1):
    data[f'Year_{i}']=[]

for index, row in donnes.iterrows() :
    for i in range(0,10): 
        if (row[f'Year_{i}']<=250 and row[f'Year_{i+1}']>=250): 
            entreprise_interet.append(index)
            date_franchissement.append(i)
            # Remplir les données avant et après la date de franchissement
            for j in range(-9, 11):  # Plage d'années normalisée autour de Year_0
                # Calculer la colonne originale correspondante
                col_idx = i + j
                if 0 <= col_idx < 11:  # S'assurer qu'on ne dépasse pas les limites des colonnes disponibles
                    # Ajouter la valeur de la ligne actuelle dans la bonne année du dictionnaire
                    data[f'Year_{j}'].append(row[f'Year_{col_idx}'])
                else:
                    # Ajouter None pour les années où il n'y a pas de données
                    data[f'Year_{j}'].append(None)
            break
            
            #si on veut avoir aussi les entreprises qui passent de ETI à PME
        """elif (row[f'Year_{i}']>=250 and row[f'Year_{i+1}']<=250):
            entreprise_interet.append(index)
            date_franchissement.append(i)
            # Remplir les données avant et après la date de franchissement
            for j in range(-9, 11):  # Plage d'années normalisée autour de Year_0
                # Calculer la colonne originale correspondante
                col_idx = i + j
                if 0 <= col_idx < 11:  # S'assurer qu'on ne dépasse pas les limites des colonnes disponibles
                    # Ajouter la valeur de la ligne actuelle dans la bonne année du dictionnaire
                    data[f'Year_{j}'].append(row[f'Year_{col_idx}'])
                else:
                    # Ajouter None pour les années où il n'y a pas de données
                    data[f'Year_{j}'].append(None)
            break"""

#print(len(entreprise_interet))
#print(len(date_franchissement))
normalisation = pd.DataFrame(data, columns=['Year_-9', 'Year_-8','Year_-7','Year_-6','Year_-5','Year_-4','Year_-3','Year_-2','Year_-1','Year_0', 'Year_1','Year_2','Year_3','Year_4','Year_5','Year_6','Year_7','Year_8','Year_9','Year_10'])
#print(normalisation.head())

# Remplir les NaN par les valeurs non NaN les plus proches
# Remplissage vers l'avant (forward fill)
normalisation = normalisation.fillna(method='ffill', axis=1)

# Remplissage vers l'arrière (backward fill)
normalisation = normalisation.fillna(method='bfill', axis=1)
# +
from sklearn.cluster import KMeans

# 1. Sélectionner les colonnes pertinentes (les données numériques que vous souhaitez regrouper)
# Supposons que 'normalisation' soit un DataFrame contenant les colonnes normalisées
X = normalisation.iloc[:, 1:].values  # Exclure la colonne 0 si c'est un identifiant

# 2. Appliquer K-means pour regrouper les lignes
n_clusters = 10  # Choisir le nombre de clusters
kmeans = KMeans(n_clusters=n_clusters, random_state=42)

# Ajouter une nouvelle colonne 'Cluster' avec les labels des clusters obtenus
normalisation['Cluster'] = kmeans.fit_predict(X)

# 3. Visualiser une partie du DataFrame
print(normalisation[18:26])


# +
# Sélectionner les colonnes en les passant sous forme de liste
mean_trajectories = normalisation.groupby('Cluster')[['Year_-9', 'Year_-8','Year_-7','Year_-6','Year_-5','Year_-4','Year_-3','Year_-2','Year_-1','Year_0', 'Year_1','Year_2','Year_3','Year_4','Year_5','Year_6','Year_7','Year_8','Year_9','Year_10']].mean()  # Moyenne des trajectoires par cluster

# 3. Tracer les courbes moyennes des clusters sur une même figure
plt.figure(figsize=(12, 6))

# Itérer sur chaque cluster pour tracer la courbe type (moyenne)
for cluster in range(n_clusters):
    plt.plot(['Year_-9', 'Year_-8','Year_-7','Year_-6','Year_-5','Year_-4','Year_-3','Year_-2','Year_-1','Year_0', 'Year_1','Year_2','Year_3','Year_4','Year_5','Year_6','Year_7','Year_8','Year_9','Year_10'], 
             mean_trajectories.loc[cluster, :], marker='o', label=f'Cluster {cluster}')

# Ajouter des labels et titre
plt.xlabel('Années')
plt.ylabel('Effectifs moyens')
plt.title('Courbes types des clusters')
plt.legend()
plt.grid(True)

# Afficher le graphique
plt.show()


# +
"""en faisant tourner le programme plusieurs fois on s'est rendu compte que parfois 
il n'y avait qu'une entreprise par cluster donc pour etre sur on affiche que les cluster signifiacatif"""

for cluster in range(n_clusters):
    print(f"""Le nombre d'entreprises appartenant au cluster {cluster} = {len(normalisation[normalisation['Cluster'] == cluster])}""")


# Compter le nombre d'entreprises par cluster
cluster_counts = normalisation['Cluster'].value_counts()

# Liste des années
years = ['-9', '-8','-7','-6','-5','-4','-3','-2','-1','0', 
         '1','2','3','4','5','6','7','8','9','10']

plt.figure(figsize=(12, 6))

# Itérer sur chaque cluster
for cluster in range(n_clusters) :
    # Vérifier s'il y a au moins 10 entreprises dans le cluster
    if cluster_counts[cluster] >= 10:
        # Tracer la courbe moyenne pour le cluster
        plt.plot(years, mean_trajectories.loc[cluster, :], marker='o', label=f'Cluster {cluster}')

# Ajouter des labels et titre
plt.xlabel('Années')
plt.ylabel('Effectifs moyens')
plt.title('Courbes types des clusters (seulement ceux avec au moins 5 entreprises)')
plt.legend()
plt.grid(True)

# Afficher le graphique

plt.show()


# -



