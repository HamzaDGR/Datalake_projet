import logging
import uuid
import pandas as pd
import mysql.connector
from mysql.connector import Error
from pymongo import MongoClient


# Configuration MySQL (staging)
MYSQL_HOST = "mysql"
MYSQL_USER = "root"
MYSQL_PASSWORD = "root"
MYSQL_DATABASE = "staging"

# Configuration MongoDB
MONGO_URI = "mongodb://host.docker.internal:27017"
MONGO_DB_NAME = "curated"
MONGO_COLLECTION_NAME = "flights"


# Fonction de connexion MySQL
def create_mysql_connection():
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )
        return connection
    except Exception as e:
        logging.error(f"Erreur de connexion MySQL : {e}")
        return None

# Étape 1 : Extraction des données MySQL (staging)
def extract_data_from_mysql():
    connection = create_mysql_connection()
    if connection:
        query = "SELECT * FROM flights"
        df = pd.read_sql(query, connection)
        connection.close()
        return df
    else:
        return None

# Fonction pour convertir les colonnes datetime et timestamp en chaînes ISO
def convert_timestamps_to_str(df):
    """
    Convertit toutes les colonnes de type datetime ou timestamp en chaînes ISO.
    """
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):  # Gère datetime et timestamp
            df[col] = df[col].apply(lambda x: x.isoformat() if pd.notnull(x) else None)
    return df

# Étape 2 : Transformation des données (staging ➝ curated)
def transform_data(df):
    if df is None or df.empty:
        logging.error("Aucune donnée à transformer.")
        return None

    try:
        # 1️⃣ Ajout d'un identifiant unique pour chaque vol
        df['flight_id'] = [str(uuid.uuid4()) for _ in range(len(df))]

        # 2️⃣ Conversion de l'altitude de mètres en pieds
        df['altitude_ft'] = df['baro_altitude'] * 3.28084

        # 3️⃣ Direction en texte
        def direction_text(angle):
            if angle < 22.5 or angle >= 337.5:
                return 'North'
            elif 22.5 <= angle < 67.5:
                return 'North-East'
            elif 67.5 <= angle < 112.5:
                return 'East'
            elif 112.5 <= angle < 157.5:
                return 'South-East'
            elif 157.5 <= angle < 202.5:
                return 'South'
            elif 202.5 <= angle < 247.5:
                return 'South-West'
            elif 247.5 <= angle < 292.5:
                return 'West'
            else:
                return 'North-West'

        df['direction'] = df['true_track'].apply(direction_text)

        # 4️⃣ Création d’un champ géolocalisation (JSON)
        df['location'] = df.apply(lambda row: {'longitude': row['longitude'], 'latitude': row['latitude']}, axis=1)

        # 5️⃣ Suppression des colonnes inutiles
        df.drop(columns=['sensors', 'squawk', 'spi', 'baro_altitude'], inplace=True)

        # 6️⃣ Convertir les colonnes datetime et timestamp en chaînes ISO
        df = convert_timestamps_to_str(df)

        logging.info("Transformation des données terminée.")
        return df.to_dict(orient='records')

    except Exception as e:
        logging.error(f"Erreur de transformation : {e}")
        return None

# Étape 3 : Chargement des données transformées vers MongoDB (curated)
def load_data_to_mongodb(data):
    try:
        # Connexion à MongoDB
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB_NAME]
        collection = db[MONGO_COLLECTION_NAME]

        # Insertion des données dans MongoDB
        collection.insert_many(data)

        logging.info("Chargement des données vers MongoDB réussi.")
    except Exception as e:
        logging.error(f"Erreur lors du chargement vers MongoDB : {e}")

# Fonction principale
def process_data():
    # Étape 1 : Extraction des données depuis MySQL
    df = extract_data_from_mysql()

    if df is None:
        logging.error("Aucune donnée à traiter.")
        return

    # Étape 2 : Transformation des données
    transformed_data = transform_data(df)

    if transformed_data is None:
        logging.error("Erreur lors de la transformation des données.")
        return

    # Étape 3 : Chargement des données dans MongoDB
    load_data_to_mongodb(transformed_data)

if __name__ == "__main__":
    process_data()