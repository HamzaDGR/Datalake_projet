from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import subprocess

# Définir le DAG d'ingestion
dag = DAG(
    'data_ingestion',
    description='Ingestion des données OpenSky dans local stack (S3)',
    schedule_interval='*/30 * * * *', # Toutes les 30 minutes
    start_date=datetime(2025, 3, 9),
    catchup=False,
    default_args={
        'owner': 'hamza',
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    }
)

# Fonction pour exécuter le script Python via subprocess
def run_ingestion_script():

     # Exécuter le script pour créer le bucket S3
    subprocess.run(["python", "/opt/airflow/scripts/s3_create_bucket.py"], check=True)
    # Exécuter le script pour ingérer les données
    subprocess.run(["python", "/opt/airflow/scripts/ingest_data.py"], check=True)


# Définir la tâche d'ingestion des données
ingest_task = PythonOperator(
    task_id='ingest_data',
    python_callable=run_ingestion_script,
    dag=dag
)
