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

# Événement lorsque le bot est prêt
@bot.event
async def on_ready():
    print(f"Bot connecté en tant que {bot.user}")
    # Chargement des cogs
    cogs_dir = os.path.join(os.path.dirname(__file__), 'cogs')
    for filename in os.listdir(cogs_dir):
        if filename.endswith('.py'):
            bot.load_extension(f'cogs.{filename[:-3]}')
            print(f'Cog {filename[:-3]} chargé.')
    # Synchronisation des commandes slash
    await bot.tree.sync()
    print("Commandes slash synchronisées.")

# Démarrage du bot
keep_alive()
bot.run(TOKEN)