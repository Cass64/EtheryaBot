from pymongo import MongoClient
import os

# Charger l'URI MongoDB depuis l'environnement de Render
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("❌ L'URI MongoDB (MONGO_URI) n'est pas défini !")

def connect_to_mongo(uri):
    """ Fonction appelée au démarrage pour confirmer la connexion. """
    try:
        global mongo_client, db, profiles_collection
        mongo_client = MongoClient(uri)
        db = mongo_client["DeltaDB"]
        profiles_collection = db["user_profiles"]
        print("✅ Connecté à MongoDB")
    except Exception as e:
        print(f"❌ Erreur lors de la connexion à MongoDB : {e}")

def get_user_profile(user_id: int):
    """ Récupère un profil utilisateur par son ID. """
    return profiles_collection.find_one({"_id": user_id})

def save_user_profile(user_id: int, data: dict):
    """ Enregistre ou met à jour un profil utilisateur. """
    profiles_collection.update_one({"_id": user_id}, {"$set": data}, upsert=True)

# Connexion MongoDB
connect_to_mongo(MONGO_URI)
