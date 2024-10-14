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


# +
# Répéter le processus de croissance sur 10 ans
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
    df.loc[zeros_indices, f'Year_{year}'] = yule_samples

# Tracer une grille de 11 sous-graphes
fig, axs = plt.subplots(4, 3, figsize=(15, 10))  # 3 lignes et 4 colonnes
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
for j in range(years + 1, 12):
    fig.delaxes(axs[j])

# Ajuster l'espacement entre les sous-graphes
plt.tight_layout()

# Afficher le graphique
plt.show()
# -

df


# +
# Tracer une grille de 11 sous-graphes
fig, axs = plt.subplots(6, 2, figsize=(15, 20))  # 3 lignes et 4 colonnes
axs = axs.flatten() 

for year in range(1, years + 1):
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
columns = ['Year_0', 'Year_1','Year_2','Year_3','Year_4','Year_5','Year_6','Year_7','Year_8','Year_9','Year_10']
df_top10 = df.head(10)[columns]

# Définir les années
years = df.columns[1:]  # Ignorer la colonne 'Entreprise'

# Tracer les effectifs des 10 premières entreprises
plt.figure(figsize=(12, 6))

for index, row in df_top10.iterrows():
    plt.plot(columns, row, marker='o')

plt.title('Effectifs des 10 Premières Entreprises par Année')
plt.xlabel('Année')
plt.ylabel('Effectif')
plt.xticks(rotation=45)  # Rotation des labels d'axes x pour une meilleure lisibilité
plt.grid(True)
plt.legend(title='Entreprises', bbox_to_anchor=(1.05, 1), loc='upper left')  # Légende à droite
plt.tight_layout()  # Ajuste l'espace pour éviter le chevauchement
plt.show()

# +
donnes= df.drop(['Growth_1','Growth_2','Growth_3','Growth_4','Growth_5','Growth_6','Growth_7','Growth_8','Growth_9','Growth_10'], axis=1)
seuil = 250
entreprise_interet=[]
date_franchissement= []

for index, row in donnes.iterrows() :
    for i in range(0,10): 
        if (donnes[index][f'Year_{i}']<=250 and donnes[index][f'Year_{i+1}']>=250): 
            entreprise_interet.append(index)
            date_franchissement.append(i)
            break
        elif (donnes[index][f'Year_{i}']>=250 and donnes[index][f'Year_{i+1}']<=250):
            entreprise_interet.append(index)
            date_franchissement.append(i)
            break

# -



# +
from sklearn.cluster import KMeans


# 1. Sélectionner les colonnes pertinentes (par exemple, les colonnes de données numériques, exclure les identifiants)
# Supposons que les colonnes numériques commencent à la 1ère colonne et que la 0e colonne soit un identifiant
X = entreprises_conservees.values  # Remplace 1 par la première colonne de données pertinentes si besoin

# 2. Appliquer K-means pour regrouper les lignes
n_clusters = 10 # Par exemple, on choisit 3 clusters
kmeans = KMeans(n_clusters=n_clusters, random_state=42)
entreprises_conservees['Cluster'] = kmeans.fit_predict(X)


entreprises_conservees[18:26]


# +
mean_trajectories = entreprises_conservees.groupby('Cluster')[columns].mean()  # Moyenne des trajectoires par cluster

# 3. Tracer les courbes moyennes des clusters sur une même figure
plt.figure(figsize=(10, 6))

# Itérer sur chaque cluster pour tracer la courbe type (moyenne)
for cluster in range(n_clusters):
    plt.plot(columns, mean_trajectories.loc[cluster, :], marker='o', label=f'Cluster {cluster}')

# Ajouter des labels et titre
plt.xlabel('Années')
plt.ylabel('Effectifs moyens')
plt.title('Courbes types des clusters')
plt.legend()
plt.grid(True)

# Afficher le graphique
plt.show()

# +
# Avant de faire les clusters il faut décaler les courbes
# -


