import os
import discord
from discord.ext import commands
from utils.database import connect_to_mongo
from keep_alive import keep_alive
import asyncio

# Charger les variables d'environnement (Render)
token = os.getenv('TOKEN_BOT_DISCORD')
MONGO_URI = os.getenv('MONGO_URI')

# Vérifications basiques
if not token:
    raise ValueError("❌ Le token Discord (TOKEN_BOT_DISCORD) n'est pas défini !")
if not MONGO_URI:
    raise ValueError("❌ L'URI MongoDB (MONGO_URI) n'est pas défini !")

# Initialiser le bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Liste des cogs à charger
initial_extensions = [
    "cogs.moderation",
    "cogs.gestion",
    "cogs.jeux",
    "cogs.compte_a_rebours",
    "cogs.profil"
]

# Charger les cogs
async def load_cogs():
    for extension in initial_extensions:
        try:
            await bot.load_extension(extension)
            print(f"✅ Cog {extension} chargé avec succès !")
        except Exception as e:
            print(f"❌ Erreur lors du chargement du cog {extension} : {e}")

# Événement quand le bot est prêt
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Connecté en tant que {bot.user}")

# Fonction principale asynchrone
async def main():
    # Connexion MongoDB
    connect_to_mongo(MONGO_URI)
    # Charger les cogs
    await load_cogs()
    # Lancer le bot
    await bot.start(token)

# Démarrer tout
if __name__ == "__main__":
    keep_alive()
    # Utilisation de asyncio.run() pour démarrer le bot
    asyncio.run(main())
