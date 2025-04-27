import os
import discord
from discord.ext import commands
from utils.database import connect_to_mongo
from keep_alive import keep_alive

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
    "cogs.compte_a_rebours"
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
    print(f"🚀 Connecté en tant que {bot.user} (ID: {bot.user.id})")
    print("------")

# Démarrer tout
if __name__ == "__main__":
    keep_alive()  # Assure que ton bot reste en ligne
    connect_to_mongo(MONGO_URI)  # Connexion à MongoDB
    bot.loop.create_task(load_cogs())  # Charger les cogs de manière asynchrone
    bot.run(token)  # Lancer le bot normalement
