from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.dagrun_operator import TriggerDagRunOperator  # Importer TriggerDagRunOperator
from datetime import datetime, timedelta
import requests
import boto3
import json
import logging
from botocore.exceptions import ClientError

# URL de l'API
api_url = "https://opensky-network.org/api/states/all"

# Fonction pour télécharger les données et les envoyer vers S3
def ingest_data():
    # Créer un logger
    logger = logging.getLogger('airflow.task')

    try:
        # Récupère les données depuis l'API
        response = requests.get(api_url)

        # Vérifie si la requête a réussi
        if response.status_code == 200:
            data = response.json()
            
            # Connexion à S3 via LocalStack 
            s3_client = boto3.client('s3', 
                                     endpoint_url="http://host.docker.internal:4566",  # LocalStack
                                     aws_access_key_id="hamza",
                                     aws_secret_access_key="hamza123",
                                     region_name="us-east-1")

            # Nom du bucket S3
            bucket_name = "open-sky-datalake-bucket"

            # Créer un nom de fichier basé sur l'heure
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"opensky_data_{timestamp}.json"

            # Envoie les données vers le bucket S3 simulé
            s3_client.put_object(
                Bucket=bucket_name,  # Le nom de votre bucket S3 simulé dans LocalStack
                Key=f"raw_data/{filename}",
                Body=json.dumps(data)
            )
            logger.info(f"Les données ont été envoyées vers S3 avec le nom {filename}")
        else:
            logger.error(f"Erreur lors de la récupération des données : {response.status_code}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur lors de la connexion à l'API OpenSky : {e}")
    except Exception as e:
        logger.error(f"Erreur inconnue : {e}")

# Définir le DAG d'ingestion
dag = DAG(
    'data_ingestion',
    description='Ingestion des données OpenSky dans local stack (S3)',
    # Exécuter toutes les 30 minutes
    schedule_interval='*/30 * * * *',  
    start_date=datetime(2025, 3, 9),
    catchup=False,
    default_args={
        'owner': 'hamza',
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    }
)

# Définir la tâche pour déclencher la validation du bucket (DAG séparé)
create_bucket_task = TriggerDagRunOperator(
    task_id='trigger_create_bucket',  # Nom de la tâche
    trigger_dag_id='s3_bucket_creation',  # Nom du DAG de validation du bucket
    conf={},  # Tu peux envoyer des paramètres si nécessaire
    dag=dag
)

# Définir la tâche d'ingestion des données
ingest_task = PythonOperator(
    task_id='ingest_data',
    python_callable=ingest_data,
    dag=dag
)

# Définir les dépendances : la tâche d'ingestion dépend de la création du bucket
create_bucket_task >> ingest_task
