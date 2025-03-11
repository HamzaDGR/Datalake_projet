# Projet Data Lake OpenSky

## Introduction
Ce projet vise à concevoir et implémenter un Data Lake en utilisant diverses technologies modernes de traitement et de stockage des données. L'objectif est de collecter, ingérer et stocker des données aéronautiques issues d'OpenSky Network, tout en permettant leur analyse via une pipeline de données automatisée.

Le projet repose sur les technologies suivantes :
- **Docker & Docker Compose** pour la gestion des services
- **Airflow** pour l'orchestration des pipelines de données
- **AWS S3 (via LocalStack)** pour le stockage des données
- **MySQL** pour le stockage relationnel des données structurées
- **MongoDB** pour le stockage NoSQL des données semi-structurées

---

## Installation

### 1. Installer les dépendances
Il est recommandé d'utiliser un environnement virtuel Python :

```sh
venv\Scripts\Activate  
pip install -r requirements.txt
```

### 2. Lancer les services Docker
Démarrez Docker, puis exécutez la commande suivante pour lancer les conteneurs :

```sh
docker-compose up --build -d
```

### 3. Installer `pymongo` dans le conteneur Airflow

```sh
docker exec -it data-lake-opensky-airflow-worker-1 bash
pip install pymongo
exit
```

---

## Utilisation

### 1. Accéder à l'interface Airflow
Ouvrez votre navigateur et connectez-vous avec les identifiants `airflow / airflow` :

```sh
http://localhost:8080/home
```

### 2. Exécuter le pipeline de données
Dans l'interface Airflow, localisez le DAG nommé **data_ingestion** et cliquez sur **Trigger DAG** sous la colonne **Actions**.

Le pipeline va automatiquement :
- Collecter les données de l'API OpenSky Network
- Stocker les données dans un bucket S3
- Charger les données dans MySQL et MongoDB

---

## Validation des données

### 1. Vérifier les fichiers dans le bucket S3
Utilisez la commande suivante pour lister les fichiers stockés :

```sh
aws --endpoint-url=http://localhost:4566 s3 ls s3://open-sky-datalake-bucket/ --recursive
```

#### 📸 Capture d’écran du stockage S3 
![Capture d’écran 2025-03-12 001409](https://github.com/user-attachments/assets/b9ab4a73-306a-47a1-bee2-d50463e2efa0)


### 2. Vérifier les données dans MySQL
Accédez au conteneur MySQL et effectuez une requête de vérification :

```sh
docker exec -it mysql mysql -u root -p 
use staging;
select * from flights limit 5;
```

#### 📸 Capture d’écran de la base de données MySQL 

![Capture d’écran 2025-03-12 001943](https://github.com/user-attachments/assets/f9209abf-f9d8-4b69-a3ee-878070f6fba2)

### 3. Vérifier les données dans MongoDB Compass
Ouvrez MongoDB Compass et connectez-vous à votre base de données pour explorer les documents.

#### 📸 Capture d’écran de MongoDB Compass 

![Capture d’écran 2025-03-12 001809](https://github.com/user-attachments/assets/0180961a-d87f-4b38-aa3d-a6e9dba8bf17)

---

## Auteurs

### 👥 Contributeurs
- **Tom-Hugues ALLARD** - [tom-hugues.allard@efrei.net](mailto:tom-hugues.allard@efrei.net)  
- **Hamza DOUGAREM** - [hamza.dougarem@laposte.net](mailto:hamza.dougarem@laposte.net)

Merci pour votre intérêt et votre retour ! 🚀




