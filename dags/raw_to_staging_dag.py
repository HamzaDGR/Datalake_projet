from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import subprocess
from logging import getLogger

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

def run_transformation_script():
    try:
        subprocess.run(["python", "/opt/airflow/scripts/raw_to_staging.py"], check=True)
    except subprocess.CalledProcessError as e:
        getLogger('airflow.task').error(f"Erreur lors de l'exécution du script : {e}")
        raise


# Définir la tâche d'exécution du script
transformation_task = PythonOperator(
    task_id='run_raw_to_staging_transformation',
    python_callable=run_transformation_script,
    dag=dag
)
