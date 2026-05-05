# BATIX - AI Command Center 🏗️🤖

Bienvenue dans le centre de commandement **BATIX**. Cette application utilise l'Intelligence Artificielle pour prédire les coûts, les délais et l'état des équipements de vos chantiers, le tout couplé à une base de données SQL pour l'historique.

## 📋 Prérequis

Avant de lancer l'application, assurez-vous d'avoir :
1.  **XAMPP** installé et lancé.
2.  **Python** (via Anaconda ou standard) installé.
3.  **Node.js** installé pour le frontend.

---

## 🚀 Guide d'Exécution (Étape par Étape)

### Étape 1 : Préparation de la Base de Données (XAMPP)
1.  Ouvrez le **XAMPP Control Panel**.
2.  Démarrez les modules **Apache** et **MySQL**.
3.  *(L'application créera automatiquement la base `construction_db` et la table `predictions` lors du premier lancement du backend).*

### Étape 2 : Lancer le Backend (FastAPI)
1.  Ouvrez un terminal dans le dossier `backend/`.
2.  Activez votre environnement Python si nécessaire.
3.  Lancez le serveur avec la commande suivante :
    ```bash
& "C:\Users\21658\anaconda3\python.exe" -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    ```
    *Le backend sera accessible sur : http://localhost:8000*

### Étape 3 : Lancer le Frontend (React/Vite)
1.  Ouvrez un nouveau terminal dans le dossier `frontend/`.
2.  Installez les dépendances (si ce n'est pas déjà fait) :
    ```bash
    npm install
    ```
3.  Lancez l'interface web :
    ```bash
    npm run dev
    ```
    *L'interface BATIX sera accessible sur : http://localhost:5173*

---

## 🛠️ Structure du Projet

*   `/backend` : Code Python FastAPI, modèles ML (.joblib) et logique SQL.
*   `/frontend` : Dashboard React avec graphiques (Recharts) et export PDF.
*   `train_and_export.py` : Script pour ré-entraîner les modèles si les données changent.
*   `construction_project_dataset_updated.csv` : Le dataset source.

---

## 💡 Fonctionnalités Clés
*   **Analyse de Budget** : Prédiction de la déviation des coûts.
*   **Forecast Planning** : Estimation des retards en jours.
*   **Radar de Risque** : Visualisation dynamique des paramètres du projet.
*   **Historique SQL** : Archivage automatique de chaque analyse.
*   **Rapport PDF** : Exportation de rapports professionnels d'un simple clic.

---
*Développé pour BATIX - Intelligence Artificielle & Analytics*
