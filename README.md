# Projet Data Lake OpenSky

## Introduction
Ce projet vise à concevoir et implémenter un Data Lake en utilisant diverses technologies modernes de traitement et de stockage des données. L'objectif est de collecter, ingérer et stocker des données aéronautiques issues d'OpenSky Network, tout en permettant leur analyse via une pipeline de données automatisée.

Le projet repose sur les technologies suivantes :
- **Docker & Docker Compose** pour la gestion des services
- **Airflow** pour l'orchestration des pipelines de données
- **AWS S3 (via LocalStack)** pour le stockage des données
- **MySQL** pour le stockage relationnel des données structurées
- **MongoDB** pour le stockage NoSQL des données semi-structurées
- **FastAPI** pour exposer les données via une API REST

## Open Sky

L'API OpenSky REST est une interface de programmation d'applications qui permet d'accéder à des données en temps réel sur les avions et leur position, collectées à partir de milliers de capteurs et radars répartis dans le monde entier. Elle offre une méthode simple et directe pour obtenir des informations liées au trafic aérien, telles que les positions, les trajets, les horaires, etc. C'est à partir de cette API que nous collecterons les données.

---

## Architecture Generale 

![architecture drawio](https://github.com/user-attachments/assets/16df8122-bb68-41ed-abbe-1ab07e5ae92b)



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
## Requêter les données via l'API

### Une API REST permet d'accéder aux données stockées dans le Data Lake.

### 1. Récupérer les données brutes depuis le bucket S3

Utilisez l'URL suivante pour accéder aux fichiers raw :

http://127.0.0.1:8000/raw/all_content?bucket=open-sky-datalake-bucket&prefix=raw_data/

![image](https://github.com/user-attachments/assets/2e16357e-c53d-4a18-bdc9-0f07726d0fb2)


### 2. Récupérer les données curées depuis MongoDB

Utilisez l'URL suivante pour interroger la collection des vols :

http://127.0.0.1:8000/curated?collection=flights

![Capture d’écran 2025-03-12 004417](https://github.com/user-attachments/assets/2fc3b038-4578-40f9-a6ac-1c838bbd8f67)

Les autres API sont en cours de developpement 

### Objectif Final : Dashboard Streamlit

L'objectif final de ce projet est de développer un dashboard interactif avec Streamlit, permettant de visualiser et d'analyser les données collectées. Ce dashboard proposera plusieurs graphiques et indicateurs clés pour mieux comprendre les tendances et les statistiques des vols aériens.



## Auteurs

### 👥 Contributeurs
- **Tom-Hugues ALLARD** - [tom-hugues.allard@efrei.net](mailto:tom-hugues.allard@efrei.net)  
- **Hamza DOUGAREM** - [hamza.dougarem@efrei.net](mailto:hamza.dougarem@efrei.net)

Merci pour votre intérêt et votre retour ! 🚀




