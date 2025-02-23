import os  
from dotenv import load_dotenv
import discord
from discord.ext import commands
from keep_alive import keep_alive
import asyncio
from pymongo import MongoClient

cooldowns = {}

# Chargement des variables d'environnement
load_dotenv()
token = os.getenv('TOKEN_BOT_DISCORD')
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
    async def on_ready(self):
        print(f"Bot connecté en tant que {self.user}")
        
        # Charger les cogs
        await self.load_cogs()
        
        # Synchroniser les commandes slash (si tu utilises des commandes slash)
        try:
            await self.tree.sync()
            print("✅ Commandes slash synchronisées.")
        except Exception as e:
            print(f"❌ Erreur de synchronisation des commandes slash : {e}")
    
    async def load_cogs(self):
        for extension in ['eco', 'moderation', 'gestion']:
            try:
                await self.load_extension(f'cogs.{extension}')
                print(f'✅ Cog {extension} chargé.')
            except Exception as e:
                print(f'❌ Erreur lors du chargement de {extension}: {e}')
            
# Intents et configuration du bot
intents = discord.Intents.all()
bot = EtheryaBot(command_prefix="!!", intents=intents)
bot.db = db  # Ajouter la base de données à l'objet bot

@bot.event
async def on_message(message):
    # Ignorer les messages envoyés par d'autres bots
    if message.author.bot:
        return

    # Vérifie si le message mentionne uniquement le bot
    if bot.user.mentioned_in(message) and message.content.strip() == f"<@{bot.user.id}>":
        embed = discord.Embed(
            title="📜 Liste des Commandes",
            description="Voici la liste des commandes disponibles :",
            color=discord.Color(0xFFFFFF)
        )

        embed.add_field(
            name="💥 `!!break <membre>`",
            value="Retire un rôle spécifique à un membre. Exemple : `!!break @Utilisateur`",
            inline=False
        )
        embed.add_field(
            name="⏳ `!!malus <membre>`",
            value="Ajoute un rôle malus à un membre pour une durée prédéfinie de 24 heures. Exemple : `!!malus @Utilisateur`",
            inline=False
        )
        embed.add_field(
            name="☠️ `!!annihilation <membre>`",
            value="Cible un membre pour l'anéantissement. Exemple : `!!annihilation @Utilisateur`",
            inline=False
        )
        embed.add_field(
            name="🌌 `!!gravity <membre>`",
            value="Ajoute le rôle 'Gravité Forte' à un membre. Exemple : `!!gravity @Utilisateur`",
            inline=False
        )
        embed.add_field(
            name="🚀 `!!spatial <membre>`",
            value="Ajoute temporairement le rôle 'Spatial' à un membre. Exemple : `!!spatial @Utilisateur`",
            inline=False
        )
        embed.add_field(
            name="🏥 `!!heal`",
            value="Retire les malus et soigne l'utilisateur exécutant la commande.",
            inline=False
        )
        embed.add_field(
            name="🛡️ `!!protect`",
            value="Protège temporairement l'utilisateur des vols. Exemple : `!!protect`",
            inline=False
        )

        embed.set_thumbnail(url="https://github.com/Cass64/EtheryaBot/blob/main/images_etherya/etheryBot_profil.jpg?raw=true")
        embed.set_footer(text="Utilise ces commandes avec sagesse !")
        embed.set_image(url="https://github.com/Cass64/EtheryaBot/blob/main/images_etherya/etheryaBot_banniere.png?raw=true")

        await message.channel.send(embed=embed)

    # Assurez-vous que le bot continue de traiter les commandes
    await bot.process_commands(message)

keep_alive()
bot.run(token)
