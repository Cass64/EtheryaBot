import os  
from dotenv import load_dotenv
import discord
from discord.ext import commands
from keep_alive import keep_alive
import asyncio
from pymongo import MongoClient

# Chargement des variables d'environnement
load_dotenv()
TOKEN = os.getenv('TOKEN_BOT_DISCORD')
MONGO_URI = os.getenv('MONGO_URI')

# Connexion MongoDB
client = MongoClient(MONGO_URI)
db = client['Cass-Eco2']

# Vérification de la connexion MongoDB
try:
    client.admin.command('ping')
    print("✅ Connexion à MongoDB réussie !")
except Exception as e:
    print(f"❌ Échec de connexion à MongoDB : {e}")
    exit()
    
class EtheryaBot(commands.Bot):
    async def setup_hooks(self):
        for extension in ['eco','moderation','gestion']:
            await self.load_extension(f'cogs.{extension}')
            
# Intents et configuration du bot
intents = discord.Intents.all()
bot = EtheryaBot(command_prefix="!!", intents=intents)
bot.db = db  # Ajouter la base de données à l'objet bot

keep_alive()
bot.run(TOKEN)