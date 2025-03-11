from fastapi import FastAPI, HTTPException, Query
from typing import Optional
import boto3
from motor.motor_asyncio import AsyncIOMotorClient
import json
from fastapi.responses import JSONResponse
import os
from pymongo import MongoClient
import pymysql


#Initialisation des clients pour les services
s3_client = boto3.client('s3', 
                             endpoint_url="http://host.docker.internal:4566",  # LocalStack
                             aws_access_key_id="hamza",
                             aws_secret_access_key="hamza123",
                             region_name="us-east-1")


# Création de l'application FastAPI
app = FastAPI()

# /raw : Accès aux données brutes dans le bucket S3
#http://127.0.0.1:8000/raw/all_content?bucket=open-sky-datalake-bucket&prefix=raw_data/
@app.get("/raw/all_content")
async def get_all_raw_content(
    bucket: str = Query(..., description="Nom du bucket S3", example="open-sky-datalake-bucket"),
    prefix: str = Query("", description="Préfixe pour filtrer les fichiers (ex: 'raw_data/')", example="raw_data/")
):
    try:
        # Lister tous les fichiers sous le préfixe donné
        response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
        files = response.get("Contents", [])

        if not files:
            raise HTTPException(status_code=404, detail="No files found in the bucket")

        all_data = []
        
        for file in files:
            file_key = file["Key"]
            
            # Lire le contenu du fichier
            file_response = s3_client.get_object(Bucket=bucket, Key=file_key)
            content = file_response["Body"].read().decode("utf-8")
            
            # Convertir en JSON et l'ajouter à la liste
            try:
                json_content = json.loads(content)
                all_data.append({"file": file_key, "data": json_content})
            except json.JSONDecodeError:
                all_data.append({"file": file_key, "data": "Invalid JSON format"})

        return all_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error accessing S3: {str(e)}")


# /curated : Accès aux données finales dans MongoDB
#http://127.0.0.1:8000/curated?collection=flights
@app.get("/curated")
async def get_curated_data(collection: str = Query(..., description="Nom de la collection dans MongoDB")):
    try:
        # Connexion à MongoDB
        client = AsyncIOMotorClient("mongodb://localhost:27017")
        db = client["curated"]  # Nom de la base de données
        
        # Vérification si la collection existe
        if collection not in await db.list_collection_names():
            raise HTTPException(status_code=404, detail=f"Collection {collection} not found")
        
        # Accéder à la collection passée en paramètre
        collection_db = db[collection]
        
        # Récupérer les données depuis MongoDB
        data = await collection_db.find().to_list(length=None)  # Récupère toutes les données
        
        if not data:
            raise HTTPException(status_code=404, detail="Aucune donnée trouvée dans la collection")
        
        # Sérialiser l'ObjectId en string
        for item in data:
            item["_id"] = str(item["_id"])  # Convertir l'ObjectId en chaîne
        
        return JSONResponse(content=data)
    
    except Exception as e:
        print(f"Erreur dans la connexion MongoDB : {str(e)}")  # Afficher l'erreur dans les logs
        raise HTTPException(status_code=500, detail=f"Error accessing MongoDB: {str(e)}")
    


