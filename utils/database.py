import motor.motor_asyncio
import os

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
        # FORCER une requête pour s'assurer que Mongo est bien connecté
        await mongo_client.server_info()
        db = mongo_client["CassBot"]
        print("✅ Connecté à MongoDB (base de données 'CassBot')")
    except Exception as e:
        print(f"❌ Erreur lors de la connexion à MongoDB : {e}")
        raise e

def get_profiles_collection():
    """Retourne la collection user_profiles."""
    if db is None:
        raise RuntimeError("❌ La base de données n'est pas connectée !")
    return db["user_profiles"]

async def get_user_profile(user_id: int):
    """Récupère un profil utilisateur par ID (async)."""
    collection = get_profiles_collection()
    return await collection.find_one({"_id": user_id})

async def save_user_profile(user_id: int, data: dict):
    """Sauvegarde ou met à jour un profil utilisateur (async)."""
    collection = get_profiles_collection()
    await collection.update_one({"_id": user_id}, {"$set": data}, upsert=True)
