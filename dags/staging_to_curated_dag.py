from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import subprocess
import logging

# Définir le DAG
dag3 = DAG(
    'mysql_to_mongodb',
    description='Pipeline de transformation des données MySQL vers MongoDB',
    schedule_interval=None,  # Ce DAG est déclenché par le DAG 2
    start_date=datetime(2025, 3, 9),
    catchup=False,
    default_args={
        'owner': 'hamza',
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    }
)

# script Python qui gère tout le processus
def run_mysql_to_mongodb_script():
    try:
        result = subprocess.run(
            ['python', '/opt/airflow/scripts/staging_to_curated.py'],
            capture_output=True, text=True
        )

        if result.returncode == 0:
            logging.info(f"Script exécuté avec succès : {result.stdout}")
        else:
            logging.error(f"Erreur lors de l'exécution du script : {result.stderr}")

    except Exception as e:
        logging.error(f"Erreur dans l'exécution du script : {e}")

# tâche d'exécution du script
process_data_task = PythonOperator(
    task_id='run_mysql_to_mongodb_script',
    python_callable=run_mysql_to_mongodb_script,
    dag=dag3
)

process_data_task  # Dernier DAG de la chaine
