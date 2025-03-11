from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dagrun_operator import TriggerDagRunOperator
from datetime import datetime, timedelta
import subprocess
from logging import getLogger

# Définir le DAG
dag2 = DAG(
    'raw_to_staging_transformation',
    description='Transformation des données OpenSky et chargement dans une BD MYSQL',
    schedule_interval=None,  # Pas de planification, il est déclenché par le DAG 1
    start_date=datetime(2025, 3, 9),
    catchup=False,
    default_args={
        'owner': 'hamza',
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    }
)

# Fonction pour exécuter le script Python via subprocess
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
    dag=dag2
)

# Définir la tâche pour déclencher le DAG 3 après la transformation
trigger_dag3 = TriggerDagRunOperator(
    task_id='trigger_dag3',
    trigger_dag_id='mysql_to_mongodb',  # ID du DAG 3
    dag=dag2
)

transformation_task >> trigger_dag3  # Transformation puis déclenchement du DAG 3
