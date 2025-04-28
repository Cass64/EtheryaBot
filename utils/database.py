import motor.motor_asyncio
import os

# Charger l'URI MongoDB depuis l'environnement de Render
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("❌ L'URI MongoDB (MONGO_URI) n'est pas défini !")

# Création du client Motor
mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = mongo_client["CassBot"]

async def test_mongo_connection():
    """Test de connexion MongoDB au démarrage."""
    try:
        await mongo_client.admin.command('ping')
        print("✅ Connecté à MongoDB")
    except Exception as e:
        print(f"❌ Erreur lors de la connexion à MongoDB : {e}")

def get_profiles_collection():
    """Retourne la collection des profils utilisateur."""
    return db["user_profiles"]

async def get_user_profile(user_id: int):
    """Récupère un profil utilisateur par son ID."""
    return await get_profiles_collection().find_one({"_id": user_id})

async def save_user_profile(user_id: int, data: dict):
    """Enregistre ou met à jour un profil utilisateur."""
    await get_profiles_collection().update_one({"_id": user_id}, {"$set": data}, upsert=True)
