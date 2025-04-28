import motor.motor_asyncio
import os
import time

# Charger l'URI MongoDB depuis l'environnement
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("❌ L'URI MongoDB (MONGO_URI) n'est pas défini !")

# Variables globales
mongo_client = None
db = None

async def connect_to_mongo(uri: str):
    """Connexion asynchrone à MongoDB au démarrage."""
    global mongo_client, db
    try:
        print("🔗 Tentative de connexion à MongoDB...")
        mongo_client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        db = mongo_client["CassBot"]
        print("✅ Connecté à MongoDB (async)")
    except Exception as e:
        print(f"❌ Erreur lors de la connexion à MongoDB : {e}")
        raise e

async def get_profiles_collection():
    """Retourne la collection user_profiles (async)."""
    if db is None:
        raise RuntimeError("❌ La base de données n'est pas connectée !")
    return db["user_profiles"]

async def get_user_profile(user_id: int):
    """Récupère un profil utilisateur par ID (async) avec logs."""
    try:
        collection = await get_profiles_collection()
        start = time.time()
        result = await collection.find_one({"_id": user_id})
        end = time.time()
        if result:
            print(f"📄 Profil trouvé pour {user_id} en {end - start:.4f} secondes : {result}")
        else:
            print(f"📄 Aucun profil trouvé pour {user_id} (temps : {end - start:.4f} secondes)")
        return result
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du profil {user_id} : {e}")
        raise e

async def save_user_profile(user_id: int, data: dict):
    """Sauvegarde ou met à jour un profil utilisateur (async) avec logs."""
    try:
        collection = await get_profiles_collection()
        start = time.time()
        result = await collection.update_one({"_id": user_id}, {"$set": data}, upsert=True)
        end = time.time()
        print(f"💾 Profil {user_id} sauvegardé en {end - start:.4f} secondes.")
        print(f"    ➔ Matched documents: {result.matched_count}, Modified documents: {result.modified_count}, Upserted ID: {result.upserted_id}")
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde du profil {user_id} : {e}")
        raise e
