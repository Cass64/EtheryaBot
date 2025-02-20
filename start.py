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
import ssl
load_dotenv()

# Connexion MongoDB
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri, ssl=True, ssl_cert_reqs=ssl.CERT_NONE)  # Connexion avec SSL
db = client['Etherya2.1']
collection = db['commande_eco']
store_collection = db['store']

# Vérification MongoDB
try:
    client.admin.command('ping')
    print("✅ Connexion à MongoDB réussie !")
except Exception as e:
    print(f"❌ Échec de connexion à MongoDB : {e}")
    exit()

cooldowns = {}

token = os.getenv('TOKEN_BOT_DISCORD')

# Intents et configuration du bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot connecté en tant que {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)

#------------------------------------------------------------------------- Commandes d'économie : /frags, /pret, /pretpayer

# Dictionnaire pour stocker les prêts en cours, maintenant persistant dans MongoDB
prets_en_cours = {}

@bot.tree.command(name="frags")
async def frags(interaction: discord.Interaction, user: discord.Member):
    """Ajoute le rôle Frags Quotidien à un utilisateur pour 24 heures."""
    # Vérifier si l'exécutant a le rôle requis
    if not any(role.name == REQUIRED_ROLE for role in interaction.user.roles):
        await interaction.response.send_message("Tu n'as pas le rôle requis pour utiliser cette commande.")
        return
    
    frag_role = discord.utils.get(interaction.guild.roles, name=FRAG_ROLE)
    if frag_role:
        await user.add_roles(frag_role)
        await interaction.response.send_message(f"Le rôle `{FRAG_ROLE}` a été attribué à {user.mention}.")

        # Retirer le rôle après 24 heures
        await asyncio.sleep(86400)  # 86400 secondes = 24 heures
        await user.remove_roles(frag_role)
        await interaction.followup.send(f"Le rôle `{FRAG_ROLE}` a été retiré de {user.mention} après 24 heures.")
    else:
        await interaction.response.send_message(f"Le rôle `{FRAG_ROLE}` n'existe pas sur ce serveur.")

@bot.tree.command(name="pret")
async def pret(interaction: discord.Interaction, membre: discord.Member, montant: int, montant_rendu: int, duree: str):
    """Enregistre un prêt avec les détails dans un salon staff."""
    await enregistrer_pret(interaction, membre, montant, montant_rendu, duree)

async def enregistrer_pret(interaction, membre, montant, montant_rendu, duree):
    """Enregistre un prêt avec détails et envoie un message dans le salon staff."""
    CHANNEL_ID = 1340674704964583455  # Remplace par l'ID du salon staff
    salon_staff = interaction.guild.get_channel(CHANNEL_ID)

    if not salon_staff:
        return await interaction.response.send_message("❌ Le salon staff n'a pas été trouvé.")

    embed = discord.Embed(title="📜 Nouveau Prêt", color=discord.Color.blue())
    embed.add_field(name="👤 Pseudonyme", value=membre.mention, inline=True)
    embed.add_field(name="💰 Montant demandé", value=f"{montant:,} crédits", inline=True)
    embed.add_field(name="📄 Ticket/Formulaire", value="Ticket", inline=True)
    embed.add_field(name="📅 Date pour rendre", value=duree, inline=True)
    embed.add_field(name="💳 Montant à rendre", value=f"{montant_rendu:,} crédits", inline=True)
    embed.add_field(name="🔄 Statut", value="En Cours", inline=True)
    embed.set_footer(text=f"Prêt enregistré par {interaction.user.display_name}")

    # Sauvegarde du prêt dans MongoDB
    prets_en_cours[membre.id] = {"montant": montant, "montant_rendu": montant_rendu, "statut": "En Cours"}
    collection.update_one({"user_id": membre.id}, {"$set": {"pret": prets_en_cours[membre.id]}}, upsert=True)

    await salon_staff.send(embed=embed)
    await interaction.response.send_message(f"✅ Prêt de {montant:,} crédits accordé à {membre.mention}. Détails envoyés aux staff.")

@bot.tree.command(name="pretpayer")
async def terminer(interaction: discord.Interaction, membre: discord.Member):
    """Marque un prêt comme 'Payé' si l'utilisateur avait un prêt en cours."""
    CHANNEL_ID = 1340674704964583455  # Remplace par l'ID du salon staff
    salon_staff = interaction.guild.get_channel(CHANNEL_ID)

    if not salon_staff:
        return await interaction.response.send_message("❌ Le salon staff n'a pas été trouvé.")

    # Vérifier si l'utilisateur a un prêt en cours dans la base de données
    user_data = collection.find_one({"user_id": membre.id})
    if not user_data or "pret" not in user_data:
        return await interaction.response.send_message(f"❌ {membre.mention} n'a aucun prêt en cours.")

    # Récupération des détails du prêt
    pret = user_data["pret"]
    montant = pret["montant"]
    montant_rendu = pret["montant_rendu"]

    # Création de l'embed pour confirmer le remboursement
    embed = discord.Embed(title="✅ Prêt Remboursé", color=discord.Color.green())
    embed.add_field(name="👤 Pseudonyme", value=membre.mention, inline=True)
    embed.add_field(name="💰 Montant demandé", value=f"{montant:,} crédits", inline=True)
    embed.add_field(name="📄 Ticket/Formulaire", value="Ticket", inline=True)
    embed.add_field(name="💳 Montant remboursé", value=f"{montant_rendu:,} crédits", inline=True)
    embed.add_field(name="🔄 Statut", value="Payé", inline=True)
    embed.set_footer(text=f"Prêt remboursé confirmé par {interaction.user.display_name}")

    # Mettre à jour le statut du prêt dans la base de données
    pret["statut"] = "Payé"
    collection.update_one({"user_id": membre.id}, {"$set": {"pret": pret}})

    await salon_staff.send(embed=embed)
    await interaction.response.send_message(f"✅ Le prêt de {montant:,} crédits de {membre.mention} est marqué comme remboursé.")

#------------------------------------------------------------------------- Commandes d'économie : !!break

# Liste des rôles autorisés pour exécuter les commandes de modération
AUTHORIZED_ROLES = ["″ [𝑺ץ] Perm Anti Protect"]

@bot.command(name="break")
async def breakk(ctx, membre: discord.Member):
    """Ajoute un rôle fixe à un utilisateur et retire un autre rôle fixe à l'exécutant.
       Seuls ceux ayant '[𝑺ץ] Perm Anti Protect' peuvent utiliser cette commande.
    """
    ROLE_REQUIRED = "″ [𝑺ץ] Perm Anti Protect"  # Rôle requis pour exécuter la commande
    ROLE_TO_REMOVE_BREAK = "″ [𝑺ץ] Protect !!rob"       # Rôle à ajouter au membre ciblé
    ROLE_TO_REMOVE = "″ [𝑺ץ] Perm Anti Protect"     # Rôle à retirer à l'exécutant

    role_required = discord.utils.get(ctx.guild.roles, name=ROLE_REQUIRED)
    role_to_remove_break = discord.utils.get(ctx.guild.roles, name=ROLE_TO_REMOVE_BREAK)
    role_to_remove = discord.utils.get(ctx.guild.roles, name=ROLE_TO_REMOVE)

    if not role_required or not role_to_remove_break or not role_to_remove:
        return await ctx.send("❌ L'un des rôles spécifiés n'existe pas.")

    if role_required not in ctx.author.roles:
        return await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")

    # Vérifie si le membre a le rôle avant de le retirer
    if role_to_remove_break not in membre.roles:
        await ctx.send(f"{membre.mention} n'a pas le rôle {role_to_remove_break.mention}. <:haram:1176229029796380702>")
    else:
        await membre.remove_roles(role_to_remove_break)
        await ctx.send(f"Le rôle {role_to_remove_break.mention} a été enlevé. <a:fete:1172810362261880873>")

    # Retirer le rôle à l'exécutant
    if role_to_remove in ctx.author.roles:
        await ctx.author.remove_roles(role_to_remove)
        await ctx.send(f"Le rôle {role_to_remove.mention} vous a été retiré. <a:emoji:1341500461475168369>")
    else:
        await ctx.send(f"{ctx.author.mention}, vous n'aviez pas le rôle {role_to_remove.mention}. ❌")

#------------------------------------------------------------------------- Commandes d'économie : !!malus

AUTHORIZED_ROLES = ["″ [𝑺ץ] Perm Ajout Malus"]

@bot.command(name="malus")
async def malus(ctx, membre: discord.Member):
    """Ajoute un rôle fixe à un utilisateur, retire un autre rôle fixe à l'exécutant, 
       et supprime le rôle ajouté après une durée spécifiée.
       Seuls ceux ayant '[𝑺ץ] Perm Ajout Malus' peuvent utiliser cette commande.
    """
    ROLE_REQUIRED = "″ [𝑺ץ] Perm Ajout Malus"  # Rôle requis pour exécuter la commande
    ROLE_TO_ADD_MALUS = "″ [𝑺ץ] Malus Temporelle"  # Le rôle temporaire à ajouter
    ROLE_TO_REMOVE_MALUS = "″ [𝑺ץ] Perm Ajout Malus"  # Rôle à retirer à l'exécutant

    role_required = discord.utils.get(ctx.guild.roles, name=ROLE_REQUIRED)
    role_to_add_malus = discord.utils.get(ctx.guild.roles, name=ROLE_TO_ADD_MALUS)
    role_to_remove_malus = discord.utils.get(ctx.guild.roles, name=ROLE_TO_REMOVE_MALUS)

    if not role_required or not role_to_add_malus or not role_to_remove_malus:
        return await ctx.send("❌ L'un des rôles spécifiés n'existe pas.")

    if role_required not in ctx.author.roles:
        return await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")

    # Ajouter le rôle temporaire à l'utilisateur
    await membre.add_roles(role_to_add_malus)
    await ctx.send(f"Le rôle {role_to_add_malus.mention} a été ajouté. <a:fete:1172810362261880873>") 

    # Retirer le rôle à l'exécutant
    if role_to_remove_malus in ctx.author.roles:
        await ctx.author.remove_roles(role_to_remove_malus)
        await ctx.send(f"Le rôle {role_to_remove_malus.mention} a été retiré. <a:emoji:1341500461475168369>")
    else:
        await ctx.send(f"{ctx.author.mention}, vous n'aviez pas le rôle {role_to_remove_malus.mention}. <:haram:1176229029796380702>")

    # Temps pendant lequel le rôle restera (exemple : 1 heure)
    await asyncio.sleep(86400)  # 86400 secondes = 24 heures

    # Retirer le rôle après le délai
    await membre.remove_roles(role_to_add_malus)
    await ctx.send(f"Le rôle {role_to_add_malus.mention} a été retiré de {membre.mention} après 24 heures. ⏳")

#------------------------------------------------------------------------- Commandes d'économie : !!annihilation

@bot.command(name="annihilation")
async def annihilation(ctx, membre: discord.Member):
    """Ajoute le rôle 'Cible D'anéantissement' à un utilisateur si l'exécutant a le rôle 'Perm Crystal D'anéantissement'.
       Un message est envoyé automatiquement dans un salon spécifique et l'exécutant perd son rôle 'Perm Crystal D'anéantissement'.
    """
    ROLE_REQUIRED = "″ [𝑺ץ] Perm Crystal D'anéantissement"  # Rôle requis pour exécuter la commande
    ROLE_TO_ADD = "″ [𝑺ץ] Cible D'anéantissement"  # Rôle à ajouter
    CHANNEL_ID = 1341844144032714833  # ID du salon où envoyer le message
    ROLE_PING = 792755123587645461

    role_required = discord.utils.get(ctx.guild.roles, name=ROLE_REQUIRED)
    role_to_add = discord.utils.get(ctx.guild.roles, name=ROLE_TO_ADD)
    channel = bot.get_channel(CHANNEL_ID)
    role_ping = discord.utils.get(ctx.guild.roles, name=ROLE_PING)

    if not role_required or not role_to_add or not channel:
        return await ctx.send("❌ L'un des rôles ou le salon spécifié n'existe pas.")

    if role_required not in ctx.author.roles:
        return await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")

    # Ajouter le rôle à la cible
    await membre.add_roles(role_to_add)
    await ctx.send(f"Le rôle {role_to_add.mention} a été ajouté à {membre.mention}. ☠️")

    # Retirer le rôle de l'exécutant
    await ctx.author.remove_roles(role_required)
    await ctx.send(f"Le rôle {role_required.mention} vous a été retiré, vous ne pouvez plus utiliser cette commande. ❌")

    # Envoyer un message dans le salon spécifié
    await channel.send(f"{membre.mention} a été ciblé par un anéantissement <@{ROLE_PING}>. ⚡")

#------------------------------------------------------------------------- Commandes d'économie : !!gravity

@bot.command(name="gravity")
async def gravity(ctx, membre: discord.Member):
    """Ajoute le rôle '″ [𝑺ץ] Gravité Forte' à un utilisateur, retire le rôle '″ [𝑺ץ] Perm Gravité Forte' de l'exécutant,
       et envoie un message confirmant l'opération.
       Seuls ceux ayant le rôle '″ [𝑺ץ] Perm Gravité Forte' peuvent utiliser cette commande.
    """
    ROLE_REQUIRED = "″ [𝑺ץ] Perm Gravité Forte"  # Rôle requis pour exécuter la commande
    ROLE_TO_ADD = "″ [𝑺ץ] Gravité Forte"  # Rôle à ajouter
    ROLE_TO_REMOVE = "″ [𝑺ץ] Perm Gravité Forte"  # Rôle à retirer à l'exécutant

    role_required = discord.utils.get(ctx.guild.roles, name=ROLE_REQUIRED)
    role_to_add = discord.utils.get(ctx.guild.roles, name=ROLE_TO_ADD)
    role_to_remove = discord.utils.get(ctx.guild.roles, name=ROLE_TO_REMOVE)

    if not role_required or not role_to_add or not role_to_remove:
        return await ctx.send("❌ L'un des rôles spécifiés n'existe pas.")

    if role_required not in ctx.author.roles:
        return await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")

    # Ajouter le rôle à la cible
    await membre.add_roles(role_to_add)
    await ctx.send(f"Le rôle {role_to_add.mention} a été ajouté à {membre.mention}. 🌌")

    # Retirer le rôle à l'exécutant
    if role_to_remove in ctx.author.roles:
        await ctx.author.remove_roles(role_to_remove)
        await ctx.send(f"Le rôle {role_to_remove.mention} vous a été retiré. ❌")
    else:
        await ctx.send(f"{ctx.author.mention}, vous n'aviez pas le rôle {role_to_remove.mention}. ❌")

#------------------------------------------------------------------------- Commandes d'économie : !!spatial

@bot.command(name="spatial")
async def spatial(ctx):
    """Ajoute temporairement le rôle '[𝑺ץ] Spatial' si l'utilisateur a '[𝑺ץ] Perm Spatial',
       et applique un cooldown de 24 heures. L'heure de la dernière utilisation est enregistrée dans la base de données MongoDB.
    """
    ROLE_REQUIRED = "″ [𝑺ץ] Perm Spatial"  # Rôle requis pour exécuter la commande
    ROLE_TO_ADD = "″ [𝑺ץ] Spatial"  # Rôle à ajouter temporairement
    COOLDOWN_DURATION = 86400  # 24 heures en secondes
    TEMP_ROLE_DURATION = 3600  # 1 heure en secondes

    role_required = discord.utils.get(ctx.guild.roles, name=ROLE_REQUIRED)
    role_to_add = discord.utils.get(ctx.guild.roles, name=ROLE_TO_ADD)

    if not role_required or not role_to_add:
        return await ctx.send("❌ L'un des rôles spécifiés n'existe pas.")

    if role_required not in ctx.author.roles:
        return await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")

    # Connexion à la base de données
    user_data = collection.find_one({"user_id": ctx.author.id})

    if user_data:
        last_used = user_data.get("last_used", 0)
    else:
        last_used = 0

    now = datetime.datetime.utcnow().timestamp()

    # Vérifier si l'utilisateur est en cooldown
    if now - last_used < COOLDOWN_DURATION:
        remaining_time = int((COOLDOWN_DURATION - (now - last_used)) / 3600)
        return await ctx.send(f"❌ Vous devez attendre encore {remaining_time} heure(s) avant de réutiliser cette commande.")

    # Ajouter le rôle temporaire
    await ctx.author.add_roles(role_to_add)
    await ctx.send(f"Le rôle {role_to_add.mention} vous a été attribué pour 1 heure. 🚀")

    # Mettre à jour l'heure de la dernière utilisation dans la base de données
    collection.update_one({"user_id": ctx.author.id}, {"$set": {"last_used": now}}, upsert=True)

    # Supprimer le rôle après 1 heure
    await asyncio.sleep(TEMP_ROLE_DURATION)
    await ctx.author.remove_roles(role_to_add)
    await ctx.send(f"Le rôle {role_to_add.mention} vous a été retiré après 1 heure. ⏳")

#------------------------------------------------------------------------- Commandes d'économie : !!heal

@bot.command(name="heal")
async def heal(ctx):
    """Supprime les rôles de malus et retire le rôle permettant d'utiliser la commande."""
    ROLE_REQUIRED = "″ [𝑺ץ] Perm Anti-Dote"  # Rôle requis pour exécuter la commande
    ROLE_TO_REMOVE_1 = "″ [𝑺ץ] Gravité Forte"  # Premier rôle à enlever
    ROLE_TO_REMOVE_2 = "″ [𝑺ץ] Malus Temporelle"  # Deuxième rôle à enlever

    role_required = discord.utils.get(ctx.guild.roles, name=ROLE_REQUIRED)
    role_to_remove_1 = discord.utils.get(ctx.guild.roles, name=ROLE_TO_REMOVE_1)
    role_to_remove_2 = discord.utils.get(ctx.guild.roles, name=ROLE_TO_REMOVE_2)

    if not role_required or not role_to_remove_1 or not role_to_remove_2:
        return await ctx.send("❌ L'un des rôles spécifiés n'existe pas.")

    if role_required not in ctx.author.roles:
        return await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")

    roles_removed = []
    
    # Vérifier et retirer les rôles si présents
    if role_to_remove_1 in ctx.author.roles:
        await ctx.author.remove_roles(role_to_remove_1)
        roles_removed.append(role_to_remove_1.name)

    if role_to_remove_2 in ctx.author.roles:
        await ctx.author.remove_roles(role_to_remove_2)
        roles_removed.append(role_to_remove_2.name)

    # Message en fonction du nombre de rôles supprimés
    if len(roles_removed) == 2:
        await ctx.send(f"✨ {ctx.author.mention}, vous avez été totalement purgé de vos blessures et malédictions ! Plus rien ne vous entrave. 🏥")
    elif len(roles_removed) == 1:
        await ctx.send(f"🌿 {ctx.author.mention}, vous avez été guéri de **{roles_removed[0]}** ! Encore un petit effort pour être totalement rétabli. 💊")
    else:
        await ctx.send(f"😂 {ctx.author.mention}, tu essaies de te soigner alors que tu n'as rien ? T'es un clown !? 🤡")

    # Retirer le rôle "Perm Anti-Dote" après l'utilisation
    await ctx.author.remove_roles(role_required)
    await ctx.send(f"🔻 {ctx.author.mention}, votre **antidote** a été retiré après utilisation.")

#------------------------------------------------------------------------- Commandes d'économie : !!protect

@bot.command(name="protect")
async def protect(ctx):
    """Ajoute temporairement le rôle '[𝑺ץ] Protect !!rob' si l'utilisateur a '[𝑺ץ] Perm Protect !!rob',
       et applique un cooldown de 48 heures.
    """
    ROLE_REQUIRED = "″ [𝑺ץ] Perm Protect !!rob"  # Rôle requis pour exécuter la commande
    ROLE_TO_ADD = "″ [𝑺ץ] Protect !!rob"  # Rôle à ajouter temporairement
    COOLDOWN_DURATION = 172800  # 48 heures en secondes
    TEMP_ROLE_DURATION = 172800  # 48 heures en secondes

    role_required = discord.utils.get(ctx.guild.roles, name=ROLE_REQUIRED)
    role_to_add = discord.utils.get(ctx.guild.roles, name=ROLE_TO_ADD)

    if not role_required or not role_to_add:
        return await ctx.send("❌ L'un des rôles spécifiés n'existe pas.")

    if role_required not in ctx.author.roles:
        return await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")

    now = datetime.datetime.utcnow().timestamp()

    # Vérifier si l'utilisateur est en cooldown dans la base de données
    user_data = collection.find_one({"user_id": ctx.author.id})

    if user_data:
        last_used = user_data.get("last_used", 0)
        time_since_last_use = now - last_used
        if time_since_last_use < COOLDOWN_DURATION:
            remaining_time = int((COOLDOWN_DURATION - time_since_last_use) / 3600)
            return await ctx.send(f"❌ Vous devez attendre encore {remaining_time} heure(s) avant de réutiliser cette commande.")
    else:
        # Si l'utilisateur n'a pas de données dans la base, l'ajouter
        collection.insert_one({"user_id": ctx.author.id, "last_used": now})

    # Ajouter le rôle temporaire
    await ctx.author.add_roles(role_to_add)
    await ctx.send(f"Le rôle {role_to_add.mention} vous a été attribué pour 2 jours. 🚀")

    # Mettre à jour l'heure d'utilisation dans la base de données
    collection.update_one({"user_id": ctx.author.id}, {"$set": {"last_used": now}}, upsert=True)

    # Supprimer le rôle après 48 heures
    await asyncio.sleep(TEMP_ROLE_DURATION)
    await ctx.author.remove_roles(role_to_add)
    await ctx.send(f"Le rôle {role_to_add.mention} vous a été retiré après 2 jours. ⏳")

#------------------------------------------------------------------------- Commandes d'économie : /embed

# L'image fixe définie dans le code
fixed_image_url = "https://example.com/ton-image-fixe.png"  # Remplace par l'URL de ton image
@client.tree.command(name="embed", description="Envoie un texte formaté avec une image")
async def customtext(interaction: discord.Interaction, texte: str, image: str = None):
    # Crée un embed
    embed = discord.Embed(description=texte, color=discord.Color.green())

    # Ajoute l'image fournie (s'il y en a une)
    if image:
        embed.set_image(url=image)

    # Ajoute l'image fixe en haut à droite (thumbnail)
    embed.set_thumbnail(url=fixed_image_url)

    # Répondre avec l'embed
    await interaction.response.send_message(embed=embed)

#------------------------------------------------------------------------- Commandes classiques pour les prêts

@bot.command(name="pret10k")
async def pret10k(ctx, membre: discord.Member):
    """Enregistre un prêt de 10k avec détails dans un salon staff."""
    await enregistrer_pret(ctx, membre, montant=10000, montant_rendu=11500, duree="1 Semaine")

@bot.command(name="pret25k")
async def pret25k(ctx, membre: discord.Member):
    """Enregistre un prêt de 25k avec détails dans un salon staff."""
    await enregistrer_pret(ctx, membre, montant=25000, montant_rendu=28750, duree="1 Semaine")

@bot.command(name="pret50k")
async def pret50k(ctx, membre: discord.Member):
    """Enregistre un prêt de 50k avec détails dans un salon staff."""
    await enregistrer_pret(ctx, membre, montant=50000, montant_rendu=57500, duree="1 Semaine")

async def enregistrer_pret(ctx, membre, montant, montant_rendu, duree):
    """Enregistre un prêt avec détails et envoie un message dans le salon staff."""
    CHANNEL_ID = 1340674704964583455  # Remplace par l'ID du salon staff
    salon_staff = bot.get_channel(CHANNEL_ID)

    if not salon_staff:
        return await ctx.send("❌ Le salon staff n'a pas été trouvé.")

    embed = discord.Embed(title="📜 Nouveau Prêt", color=discord.Color.blue())
    embed.add_field(name="👤 Pseudonyme", value=membre.mention, inline=True)
    embed.add_field(name="💰 Montant demandé", value=f"{montant:,} crédits", inline=True)
    embed.add_field(name="📄 Ticket/Formulaire", value="Ticket", inline=True)
    embed.add_field(name="📅 Date pour rendre", value=duree, inline=True)
    embed.add_field(name="💳 Montant à rendre", value=f"{montant_rendu:,} crédits", inline=True)
    embed.add_field(name="🔄 Statut", value="En Cours", inline=True)
    embed.set_footer(text=f"Prêt enregistré par {ctx.author.display_name}")

    # Sauvegarde du prêt dans MongoDB
    prets_en_cours[membre.id] = {"montant": montant, "montant_rendu": montant_rendu, "statut": "En Cours"}
    collection.update_one({"user_id": membre.id}, {"$set": {"pret": prets_en_cours[membre.id]}}, upsert=True)

    await salon_staff.send(embed=embed)
    await ctx.send(f"✅ Prêt de {montant:,} crédits accordé à {membre.mention}. Détails envoyés aux staff.")

@bot.command(name="terminer")
async def terminer(ctx, membre: discord.Member):
    """Marque un prêt comme 'Payé' si l'utilisateur avait un prêt en cours."""
    CHANNEL_ID = 1340674704964583455  # Remplace par l'ID du salon staff
    salon_staff = bot.get_channel(CHANNEL_ID)

    if not salon_staff:
        return await ctx.send("❌ Le salon staff n'a pas été trouvé.")

    # Vérifier si l'utilisateur a un prêt en cours dans la base de données
    user_data = collection.find_one({"user_id": membre.id})
    if not user_data or "pret" not in user_data:
        return await ctx.send(f"❌ {membre.mention} n'a aucun prêt en cours.")

    # Récupération des détails du prêt
    pret = user_data["pret"]
    montant = pret["montant"]
    montant_rendu = pret["montant_rendu"]

    # Création de l'embed pour confirmer le remboursement
    embed = discord.Embed(title="✅ Prêt Remboursé", color=discord.Color.green())
    embed.add_field(name="👤 Pseudonyme", value=membre.mention, inline=True)
    embed.add_field(name="💰 Montant demandé", value=f"{montant:,} crédits", inline=True)
    embed.add_field(name="📄 Ticket/Formulaire", value="Ticket", inline=True)
    embed.add_field(name="💳 Montant remboursé", value=f"{montant_rendu:,} crédits", inline=True)
    embed.add_field(name="🔄 Statut", value="Payé", inline=True)
    embed.set_footer(text=f"Prêt remboursé confirmé par {ctx.author.display_name}")

    # Mettre à jour le statut du prêt dans la base de données
    pret["statut"] = "Payé"
    collection.update_one({"user_id": membre.id}, {"$set": {"pret": pret}})

    await salon_staff.send(embed=embed)
    await ctx.send(f"✅ Le prêt de {montant:,} crédits de {membre.mention} est marqué comme remboursé.")

#------------------------------------------------------------------------- Ignorer les messages des autres bots

@bot.event
async def on_message(message):
    # Ignorer les messages envoyés par d'autres bots
    if message.author.bot:
        return

    # Vérifie si le message mentionne le bot seul
    if bot.user.mentioned_in(message) and message.content.strip() == f"<@{bot.user.id}>":
        embed = discord.Embed(
            title="📜 Liste des Commandes",
            description="Voici la liste des commandes disponibles :",
            color=discord.Color(0xFFFFFF)
        )

        embed.add_field(name="💥 `!!break`", value="Retire un rôle spécifique à un membre.", inline=False)
        embed.add_field(name="⏳ `!!malus`", value="Ajoute un rôle temporaire à un membre.", inline=False)
        embed.add_field(name="☠️ `!!annihilation`", value="Cible un membre pour l'anéantissement.", inline=False)
        embed.add_field(name="🌌 `!!gravity`", value="Ajoute le rôle 'Gravité Forte' à un membre.", inline=False)
        embed.add_field(name="🚀 `!!spatial`", value="Ajoute temporairement le rôle 'Spatial'.", inline=False)
        embed.add_field(name="🏥 `!!heal`", value="Retire les malus et soigne l'utilisateur.", inline=False)
        embed.add_field(name="🛡️ `!!protect`", value="Te protège des rob temporairement.", inline=False)

        embed.set_thumbnail(url="https://github.com/Cass64/EtheryaBot/blob/main/images_etherya/etheryBot_profil.jpg?raw=true")
        embed.set_footer(text="Utilise ces commandes avec sagesse !")
        embed.set_image(url="https://github.com/Cass64/EtheryaBot/blob/main/images_etherya/etheryaBot_banniere.png?raw=true")

        await message.channel.send(embed=embed)

    # Assurez-vous que le bot continue de traiter les commandes
    await bot.process_commands(message)

#------------------------------------------------------------------------- Lancement du bot
keep_alive()
bot.run(token)
