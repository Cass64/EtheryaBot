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

#------------------------------------------------------------------------- Commandes de modération : addrole et removerole

from discord.ext import commands

# Liste des rôles autorisés pour exécuter les commandes de modération
AUTHORIZED_ROLES = ["″ [𝑺ץ] Perm Anti Protect"]

@bot.command(name="break")
async def breakk(ctx, membre: discord.Member):
    """Ajoute un rôle fixe à un utilisateur et retire un autre rôle fixe à l'exécutant.
       Seuls ceux ayant '[𝑺ץ] Perm Anti Protect' peuvent utiliser cette commande.
    """

    ROLE_REQUIRED = "″ [𝑺ץ] Perm Anti Protect"  # Rôle requis pour exécuter la commande
    ROLE_TO_REMOVE_MALUS = "″ [𝑺ץ] Protect !!rob"       # Rôle à ajouter au membre ciblé
    ROLE_TO_REMOVE = "″ [𝑺ץ] Perm Anti Protect"     # Rôle à retirer à l'exécutant

    role_required = discord.utils.get(ctx.guild.roles, name=ROLE_REQUIRED)
    role_to_remove_malus = discord.utils.get(ctx.guild.roles, name=ROLE_TO_REMOVE_MALUS)
    role_to_remove = discord.utils.get(ctx.guild.roles, name=ROLE_TO_REMOVE)

    if not role_required or not role_to_remove_malus or not role_to_remove:
        return await ctx.send("❌ L'un des rôles spécifiés n'existe pas.")

    if role_required not in ctx.author.roles:
      return await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")

# Vérifie si le membre a le rôle avant de le retirer
    if role_to_remove_malus not in membre.roles:
        await ctx.send(f"{membre.mention} n'a pas le rôle {role_to_remove_malus.mention}. <:haram:1176229029796380702>")
    else:
        await membre.remove_roles(role_to_remove_malus)
        await ctx.send(f"Le rôle {role_to_remove_malus.mention} a été enlevé. <a:fete:1172810362261880873>")


    # Retirer le rôle à l'exécutant
    if role_to_remove in ctx.author.roles:
        await ctx.author.remove_roles(role_to_remove)
        await ctx.send(f"Le rôle {role_to_remove.mention} vous a été retiré. <a:emoji:1341500461475168369>")
    else:
        await ctx.send(f"{ctx.author.mention}, vous n'aviez pas le rôle {role_to_remove.mention}. ❌")


#------------------------------------------------------------------------- Lancement du bot
keep_alive()
bot.run(token)
