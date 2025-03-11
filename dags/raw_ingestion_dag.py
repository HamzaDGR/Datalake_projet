from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dagrun_operator import TriggerDagRunOperator
from datetime import datetime, timedelta
import subprocess

# Définir le DAG d'ingestion
dag1 = DAG(
    'data_ingestion',
    description='Ingestion des données OpenSky dans local stack (S3)',
    schedule_interval='*/30 * * * *',  # Toutes les 30 minutes
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
    subprocess.run(["python", "/opt/airflow/scripts/s3_create_bucket.py"], check=True)
    subprocess.run(["python", "/opt/airflow/scripts/ingest_data.py"], check=True)

# Définir la tâche d'ingestion des données
ingest_task = PythonOperator(
    task_id='ingest_data',
    python_callable=run_ingestion_script,
    dag=dag1
)

# Définir la tâche pour déclencher le DAG 2 après ingestion
trigger_dag2 = TriggerDagRunOperator(
    task_id='trigger_dag2',
    trigger_dag_id='raw_to_staging_transformation',  # ID du DAG 2
    dag=dag1
)

ingest_task >> trigger_dag2  # Ingestion puis déclenchement du DAG 2
