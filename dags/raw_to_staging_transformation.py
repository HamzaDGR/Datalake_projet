from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import boto3
import json
import pandas as pd
import logging
from botocore.exceptions import ClientError
import mysql.connector
from mysql.connector import Error

# Configuration S3
s3_client = boto3.client('s3', 
                         endpoint_url="http://host.docker.internal:4566",  # LocalStack
                         aws_access_key_id="hamza",
                         aws_secret_access_key="hamza123",
                         region_name="us-east-1")

bucket_name = "open-sky-datalake-bucket"
raw_data_prefix = "raw_data/"
staging_data_prefix = "staging_data/"

# Connexion MySQL
MYSQL_HOST = "mysql"
MYSQL_USER = "root"
MYSQL_PASSWORD = "root"
MYSQL_DATABASE = "staging"

def create_mysql_connection():
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )
        return connection
    except Error as e:
        logging.error(f"Erreur de connexion à MySQL: {e}")
        return None

def create_table():
    connection = create_mysql_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS flights (
                id INT AUTO_INCREMENT PRIMARY KEY,
                icao24 VARCHAR(10),
                callsign VARCHAR(50),
                origin_country VARCHAR(50),
                time_position DATETIME,
                last_contact DATETIME,
                longitude FLOAT,
                latitude FLOAT,
                baro_altitude FLOAT,
                on_ground BOOLEAN,
                velocity FLOAT,
                true_track FLOAT,
                vertical_rate FLOAT,
                sensors INT,
                geo_altitude FLOAT,
                squawk VARCHAR(10),
                spi BOOLEAN,
                position_source INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        connection.commit()
        cursor.close()
        connection.close()

# Fonction pour charger les données depuis le bucket S3
def load_raw_data_from_s3():
    logger = logging.getLogger('airflow.task')

    try:
        # Lister les fichiers dans le préfixe "raw_data/"
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=raw_data_prefix)

        if 'Contents' not in response:
            logger.error("Aucun fichier brut trouvé dans le bucket S3.")
            return None

        # Prendre le dernier fichier ajouté
        latest_file = sorted(response['Contents'], key=lambda x: x['LastModified'], reverse=True)[0]
        file_key = latest_file['Key']

        # Télécharger le fichier depuis S3
        file_obj = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        raw_data = json.loads(file_obj['Body'].read().decode('utf-8'))

        logger.info(f"Fichier brut téléchargé : {file_key}")
        return raw_data
    except ClientError as e:
        logger.error(f"Erreur lors de la récupération des données depuis S3 : {e}")
        return None

def transform_raw_to_staging(**kwargs):
    logger = logging.getLogger('airflow.task')
    raw_data = kwargs['ti'].xcom_pull(task_ids='load_raw_data_from_s3')

    if raw_data is None:
        logger.error("Aucune donnée brute disponible pour la transformation.")
        return None

    try:
        # Convertir les données en DataFrame
        df = pd.DataFrame(raw_data['states'])

        # Définir les colonnes 
        df.columns = ['icao24', 'callsign', 'origin_country', 'time_position', 'last_contact', 'longitude', 
                      'latitude', 'baro_altitude', 'on_ground', 'velocity', 'true_track', 'vertical_rate', 
                      'sensors', 'geo_altitude', 'squawk', 'spi', 'position_source']

        # 1. Gestion des valeurs manquantes pour les colonnes critiques
        df['icao24'] = df['icao24'].fillna('Unknown')
        df['callsign'] = df['callsign'].fillna('Unknown')
        df['origin_country'] = df['origin_country'].fillna('Unknown')
        df['baro_altitude'] = df['baro_altitude'].fillna(0.0)
        df['time_position'] = df['time_position'].fillna(0.0)
        df['last_contact'] = df['last_contact'].fillna(0.0)
        df['on_ground'] = df['on_ground'].fillna(False)
        df['true_track'] = df['true_track'].fillna(0.0)
        df['squawk'] = df['squawk'].fillna('0000')
        df['spi'] = df['spi'].fillna(False)
        df['position_source'] = df['position_source'].fillna(0)
        df['velocity'] = df['velocity'].fillna(0.0)
        df['longitude'] = df['longitude'].fillna(0.0)
        df['latitude'] = df['latitude'].fillna(0.0)
        df['vertical_rate'] = df['vertical_rate'].fillna(0.0)
        df['sensors'] = df['sensors'].fillna(0)
        df['geo_altitude'] = df['geo_altitude'].fillna(0.0)

        # 2. Convertir les timestamps Unix en datetime et gérer les erreurs
        df['time_position'] = pd.to_datetime(df['time_position'], unit='s', errors='coerce')
        df['last_contact'] = pd.to_datetime(df['last_contact'], unit='s', errors='coerce')

        # 3. Conversion des types numériques en float
        df['longitude'] = df['longitude'].astype(float)
        df['latitude'] = df['latitude'].astype(float)
        df['velocity'] = df['velocity'].astype(float)
        df['vertical_rate'] = df['vertical_rate'].astype(float)
        df['baro_altitude'] = df['baro_altitude'].astype(float)

        # 4. Transformation de la colonne `on_ground` en booléen
        df['on_ground'] = df['on_ground'].astype(bool)
        df['spi'] = df['spi'].astype(bool)

        # 6. Supprimer les enregistrements avec des données critiques manquantes (longitude, latitude, velocity)
        df = df.dropna(subset=['longitude', 'latitude', 'velocity'], how='all')

        # 7. Remplir toute autre valeur restante `NaN` dans le dataframe avec des valeurs par défaut
        df = df.fillna({
            'callsign': 'Unknown',
            'geo_altitude': 0.0,
            'baro_altitude': 0.0,
            'on_ground': False
        })

        logger.info("Transformation des données terminée.")
        return df

    except Exception as e:
        logger.error(f"Erreur lors de la transformation des données : {e}")
        return None


def load_data_to_mysql(**kwargs):
    df = kwargs['ti'].xcom_pull(task_ids='transform_raw_data_to_staging')

    if df is None:
        logging.error("Aucune donnée à insérer dans MySQL.")
        return
    
    connection = create_mysql_connection()
    if connection:
        cursor = connection.cursor()

        # Assurez-vous que toutes les valeurs 'NaN' sont converties en 'None'
        df = df.where(pd.notnull(df), None)

        # Vérifiez à nouveau si des NaN subsistent avant insertion
        if df.isnull().values.any():
            logging.error(f"Le DataFrame contient des valeurs 'NaN' ou 'None'. Voici un aperçu : \n{df[df.isnull().any(axis=1)]}")
            return

        # Préparer la requête d'insertion
        insert_query = """
            INSERT INTO flights (icao24, callsign, origin_country, time_position, last_contact, longitude, 
                      latitude, baro_altitude, on_ground, velocity, true_track, vertical_rate, 
                      sensors, geo_altitude, squawk, spi, position_source)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        values = df[['icao24', 'callsign', 'origin_country', 'time_position', 'last_contact', 'longitude', 
                      'latitude', 'baro_altitude', 'on_ground', 'velocity', 'true_track', 'vertical_rate', 
                      'sensors', 'geo_altitude', 'squawk', 'spi', 'position_source']].values.tolist()


        # Insertion des données
        cursor.executemany(insert_query, values)
        connection.commit()
        cursor.close()
        connection.close()
        logging.info(f"Insertion terminée avec succès.")

# Définir le DAG
dag = DAG(
    'raw_to_staging_transformation',
    description='Transformation des données OpenSky et chargement dans une BD MYSQL',
    schedule_interval='@hourly',  # Exécuter toutes les heures 
    start_date=datetime(2025, 3, 9),
    catchup=False,
    default_args={
        'owner': 'hamza',
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    }
)

# Définir les tâches
load_raw_task = PythonOperator(
    task_id='load_raw_data_from_s3',
    python_callable=load_raw_data_from_s3,
    dag=dag
)

transform_data_task = PythonOperator(
    task_id='transform_raw_data_to_staging',
    python_callable=transform_raw_to_staging,
    provide_context=True,
    dag=dag
)

create_table_task = PythonOperator(
    task_id='create_mysql_table',
    python_callable=create_table,
    dag=dag
)

load_mysql_task = PythonOperator(
    task_id='load_data_to_mysql',
    python_callable=load_data_to_mysql,
    provide_context=True,
    dag=dag
)

# Définir les dépendances des tâches
load_raw_task >> transform_data_task >> create_table_task >> load_mysql_task
