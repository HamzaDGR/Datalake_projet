import requests
import boto3
import json
from datetime import datetime
import logging

def ingest_data():
    # Créer un logger
    logger = logging.getLogger('airflow.task')

    # URL de l'API
    api_url = "https://opensky-network.org/api/states/all"

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
                Bucket=bucket_name,  # Le nom de ton bucket S3
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

if __name__ == "__main__":
    ingest_data()
