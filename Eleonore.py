import scipy.special as sc
import matplotlib.pyplot as plt
import numpy as np
import pandas as 

# +
import numpy as np
import matplotlib.pyplot as plt
import scipy.special as sc

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

df = pd.DataFrame(samples, columns=['Valeur_k'])
df


