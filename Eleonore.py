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
# -

df = pd.DataFrame(samples, columns=['Year_0'])
df


# Distribution de croissance des entreprises
def laplace_distribution (g,a): 
    return np.exp(-np.abs(g)/a)/(2*a)


# +
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
a = 4 # Tu peux changer cette valeur pour tester d'autres cas

# Générer des échantillons
samples = generate_laplace_samples(a)

# Créer un DataFrame pour stocker les échantillons
df['Growth_0']= samples

# Afficher un histogramme des échantillons
plt.figure(figsize=(10, 6))
plt.hist(df['Growth_0'], bins=50, density=True, alpha=0.6, color='g')

# Calculer et tracer la distribution de Laplace pour la valeur de a choisie
g_values = np.linspace(-10, 10, 1000)
laplace_values = laplace_distribution(g_values, a)
plt.plot(g_values, laplace_values, color='r', lw=2, label=f'Distribution de Laplace (a={a})')

# Configurer le graphique
plt.title(f'Échantillons générés selon la distribution de Laplace (a = {a})')
plt.xlabel('Valeur')
plt.ylabel('Densité')
plt.legend()
plt.grid(True)

# Afficher le graphique
plt.show()

# -

df

# +
df['Year_1'] = df['Year_0']*(100+df['Growth_0'])/100

# Trouver les index où les valeurs dans "Next_Year" sont inférieures à 1
less_than_one_indices = df[df['Year_1'] < 1].index

# Remplacer les valeurs inférieures à 1 par 0
df.loc[less_than_one_indices, 'Year_1'] = 0
print (len(less_than_one_indices))
# -

df

df['Year_1']=df ['Year_1'].round().astype(int)
df

yule_samples = generate_yule_samples(rho1, size=len(less_than_one_indices))
df.loc[less_than_one_indices, 'Year_1'] = yule_samples
df




