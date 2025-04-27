import os
import discord
from discord.ext import commands
from utils.database import connect_to_mongo

# Charger les variables d'environnement (Render)
token = os.getenv('TOKEN_BOT_DISCORD')
MONGO_URI = os.getenv('MONGO_URI')

# Vérifications basiques
if not token:
    raise ValueError("❌ Le token Discord (DISCORD_TOKEN) n'est pas défini !")
if not MONGO_URI:
    raise ValueError("❌ L'URI MongoDB (MONGO_URI) n'est pas défini !")

# Connexion à MongoDB
connect_to_mongo(MONGO_URI)

# Initialiser le bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Liste des cogs à charger
initial_extensions = [
    "cogs.moderation",
    "cogs.gestion",
    "cogs.jeux"
]

# Charger les cogs
for extension in initial_extensions:
    try:
        bot.load_extension(extension)
        print(f"✅ Cog {extension} chargé avec succès !")
    except Exception as e:
        print(f"❌ Erreur lors du chargement du cog {extension} : {e}")

# Événement quand le bot est prêt
@bot.event
async def on_ready():
    print(f"🚀 Connecté en tant que {bot.user} (ID: {bot.user.id})")
    print("------")

# Démarrer le bot
bot.run(token)
