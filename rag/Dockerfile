# Utiliser une image Python officielle
FROM python:3.10-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier le fichier des dépendances
COPY requirements.txt .

# Installer les dépendances
# --no-cache-dir pour ne pas conserver le cache et alléger l'image
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code de l'application
COPY . .

# Exposer le port sur lequel l'application va tourner
EXPOSE 8001

# Commande pour lancer l'application avec Uvicorn
# --host 0.0.0.0 pour rendre le serveur accessible depuis l'extérieur du conteneur
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]