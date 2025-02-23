import os  
from dotenv import load_dotenv
from discord import app_commands
import discord
from discord.ext import commands
from keep_alive import keep_alive
import random
import json
import asyncio
import pymongo
from pymongo import MongoClient
import datetime
import math

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

# Intents et configuration du bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!!", intents=intents)
bot.db = db  # Ajouter la base de données à l'objet bot

async def load_cogs():
    cogs_dir = os.path.join(os.path.dirname(__file__), 'cogs')
    for filename in os.listdir(cogs_dir):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')  # Ajout de await
                print(f'✅ Cog {filename[:-3]} chargé.')
            except Exception as e:
                print(f'❌ Erreur lors du chargement de {filename}: {e}')

@bot.event
async def on_ready():
    print(f"Bot connecté en tant que {bot.user}")

    # Charger les cogs
    await load_cogs()

    # Synchroniser les commandes slash
    try:
        await bot.tree.sync()
        print("✅ Commandes slash synchronisées.")
    except Exception as e:
        print(f"❌ Erreur de synchronisation des commandes slash : {e}")

    # 🔥 Debug: Vérifie si les commandes existent
    print("📌 Liste des commandes chargées:")
    for command in bot.commands:
        print(f"🔹 {command.name}")

# Démarrage du bot
keep_alive()
bot.run(TOKEN)
