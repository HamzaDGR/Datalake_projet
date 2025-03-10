from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import boto3
from botocore.exceptions import ClientError

# Nom du bucket S3
bucket_name = "open-sky-datalake-bucket"

def create_s3_bucket_if_not_exists(bucket_name):
    # Créer un client S3 pour LocalStack
    s3_client = boto3.client('s3', 
                             endpoint_url="http://host.docker.internal:4566",  # LocalStack
                             aws_access_key_id="hamza",
                             aws_secret_access_key="hamza123",
                             region_name="us-east-1")
    
    try:
        # Liste tous les buckets et vérifie si le bucket existe déjà
        response = s3_client.list_buckets()
        existing_buckets = [bucket['Name'] for bucket in response['Buckets']]
        if bucket_name in existing_buckets:
            print(f"Le bucket {bucket_name} existe déjà.")
        else:
            print(f"Le bucket {bucket_name} n'existe pas, création en cours...")
            s3_client.create_bucket(Bucket=bucket_name)
            print(f"Le bucket {bucket_name} a été créé.")
    except ClientError as e:
        print(f"Erreur lors de la connexion à S3 : {e}")
        raise e

# Définir le DAG
dag = DAG(
    's3_bucket_creation',
    description='Création d\'un bucket S3 si il n\'existe pas',
    schedule_interval=None,  # DAG exécuté manuellement
    start_date=datetime(2025, 3, 9),
    catchup=False,
    default_args={
        'owner': 'hamza',
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    }
)

# Définir la tâche de création du bucket
create_bucket_task = PythonOperator(
    task_id='create_s3_bucket',
    python_callable=create_s3_bucket_if_not_exists,
    op_args=[bucket_name],
    dag=dag
)
