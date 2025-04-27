from pymongo import MongoClient
import os

# Connexion à MongoDB
MONGO_URI = os.getenv("MONGO_URI")
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["DeltaDB"]  # Tu peux changer le nom ici
profiles_collection = db["user_profiles"]

def get_user_profile(user_id: int):
    """ Récupère un profil utilisateur par son ID. """
    return profiles_collection.find_one({"_id": user_id})

def save_user_profile(user_id: int, data: dict):
    """ Enregistre ou met à jour un profil utilisateur. """
    profiles_collection.update_one({"_id": user_id}, {"$set": data}, upsert=True)

def connect_to_mongo(uri):
    """ Fonction appelée au démarrage pour confirmer la connexion. """
    global mongo_client, db, profiles_collection
    mongo_client = MongoClient(uri)
    db = mongo_client["DeltaDB"]
    profiles_collection = db["user_profiles"]
    print("✅ Connecté à MongoDB")
