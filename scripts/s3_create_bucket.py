import boto3
from botocore.exceptions import ClientError

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
        raise e  # Re-raise the error to propagate it to the calling process

if __name__ == "__main__":
    create_s3_bucket_if_not_exists('open-sky-datalake-bucket')
