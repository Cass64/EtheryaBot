import os
import discord
from discord.ext import commands
from utils.database import connect_to_mongo
from keep_alive import keep_alive
import asyncio
from birthday_tasks import init_birthday_task

# Charger les variables d'environnement
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

async def load_cogs():
    print("🔄 Chargement des cogs...")
    for extension in initial_extensions:
        try:
            await bot.load_extension(extension)
            print(f"✅ Cog {extension} chargé avec succès !")
        except Exception as e:
            print(f"❌ Erreur lors du chargement du cog {extension} : {e}")

@bot.event
async def on_ready():
    print(f"🔗 Synchronisation des commandes...")
    await bot.tree.sync()
    print(f"✅ Connecté en tant que {bot.user}")
    init_birthday_task(bot)

def main():
    # Démarrer l'asynchrone proprement
    asyncio.run(start_bot())

async def start_bot():
    print("🔗 Connexion à MongoDB...")
    await connect_to_mongo(MONGO_URI)  # Utilisation de await ici
    print("✅ Connexion à MongoDB réussie.")

    await load_cogs()  # Chargement des cogs
    await bot.start(token)

if __name__ == "__main__":
    keep_alive()
    main()
