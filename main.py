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
    
# Configuration du bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!!", intents=intents)
bot.db = db  # Ajouter la base de données à l'objet bot

# Charger les cogs
async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"✅ Cog {filename[:-3]} chargé.")
            except Exception as e:
                print(f"❌ Erreur lors du chargement de {filename} : {e}")

@bot.event
async def on_ready():
    print(f"✅ Bot connecté en tant que {bot.user}")

    # Charger les cogs
    await load_cogs()

    # Synchroniser les commandes slash
    try:
        await bot.tree.sync()
        print("✅ Commandes slash synchronisées avec succès !")
    except Exception as e:
        print(f"❌ Erreur lors de la synchronisation des commandes slash : {e}")

    # Afficher les commandes chargées
    print("📌 Liste des commandes textuelles (!!command) :")
    for command in bot.commands:
        print(f"🔹 {command.name}")

    print("📌 Liste des commandes slash (/command) :")
    for command in bot.tree.get_commands():
        print(f"🔹 {command.name}")

# Lancer le bot
keep_alive()
bot.run(TOKEN)
