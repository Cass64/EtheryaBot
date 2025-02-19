import os  
from dotenv import load_dotenv
import discord
from discord import app_commands
from discord.ext import commands
import random
from keep_alive import keep_alive
import json
import asyncio


load_dotenv()


token = os.getenv('TOKEN_BOT_DISCORD')

# Intents et configuration du bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot connecté en tant que {bot.user}")

#------------------------------------------------------------------------- Commandes d'économie : !!break

from discord.ext import commands

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
       Seuls ceux ayant '[𝑺ץ] Perm Anti Protect' peuvent utiliser cette commande.
    """

    ROLE_REQUIRED_MALUS = "″ [𝑺ץ] Perm Ajout Malus"  # Rôle requis pour exécuter la commande
    ROLE_TO_ADD_MALUS = "″ [𝑺ץ] Malus Temporelle"  # Le rôle temporaire à ajouter
    ROLE_TO_REMOVE_MALUS = "″ [𝑺ץ] Perm Ajout Malus"  # Rôle à retirer à l'exécutant

    role_required_malus = discord.utils.get(ctx.guild.roles, name=ROLE_REQUIRED_MALUS)
    role_to_add_malus = discord.utils.get(ctx.guild.roles, name=ROLE_TO_ADD_MALUS)
    role_to_remove_malus = discord.utils.get(ctx.guild.roles, name=ROLE_TO_REMOVE_MALUS)

    if not role_required_malus or not role_to_add_malus or not role_to_remove_malus:
        return await ctx.send("❌ L'un des rôles spécifiés n'existe pas.")

    if role_required_malus not in ctx.author.roles:
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
    await asyncio.sleep(86400)  # 3600 secondes = 1 heure

    # Retirer le rôle après le délai
    await membre.remove_roles(role_to_add_malus)
    await ctx.send(f"Le rôle {role_to_add_malus.mention} a été retiré de {membre.mention} après 1 jour. ⏳")

#------------------------------------------------------------------------- Commandes d'économie : !!annihilation

@bot.command(name="annihilation")
async def annihilation(ctx, membre: discord.Member):
    """Ajoute le rôle 'Cible D'anéantissement' à un utilisateur si l'exécutant a le rôle 'Perm Crystal D'anéantissement'.
       Un message est envoyé automatiquement dans un salon spécifique et l'exécutant perd son rôle 'Perm Crystal D'anéantissement'.
    """
    
    ROLE_REQUIRED = "″ [𝑺ץ] Perm Crystal D'anéantissement"  # Rôle requis pour exécuter la commande
    ROLE_TO_ADD = "″ [𝑺ץ] Cible D'anéantissement"  # Rôle à ajouter
    CHANNEL_ID = 1341844144032714833  # ID du salon où envoyer le message

    role_required = discord.utils.get(ctx.guild.roles, name=ROLE_REQUIRED)
    role_to_add = discord.utils.get(ctx.guild.roles, name=ROLE_TO_ADD)
    channel = bot.get_channel(CHANNEL_ID)

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
    await channel.send(f"{membre.mention} a été ciblé par un anéantissement <@&⁂       　Pôle Directionnel　　　⁂>. ⚡")

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

#------------------------------------------------------------------------- Ignorer les messages des autres bots

@bot.event
async def on_message(message):
    # Ignorer les messages envoyés par d'autres bots
    if message.author.bot:
        return

    # Vérifie si le message mentionne le bot
    if bot.user.mentioned_in(message):
        # Envoie un message avec le préfixe du bot
        await message.channel.send(f"<a:piece:1289678641982210059> Mon préfixe sur ce serveur est: {bot.command_prefix}" <:dab:1168325108595687434> !)

    # Assurez-vous que le bot continue de traiter les commandes
    await bot.process_commands(message)
    
#------------------------------------------------------------------------- Lancement du bot
keep_alive()
bot.run(token)
