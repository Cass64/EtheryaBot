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

load_dotenv()

cooldowns = {}

class gestion(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db  # Stocke la référence à la base de données
        
@commands.command(name="serverinfo")
    async def serverinfo(self, ctx):
        """Affiche des informations sur le serveur."""
        server_name = ctx.guild.name
        member_count = ctx.guild.member_count
        await ctx.send(f"Le serveur **{server_name}** compte {member_count} membres.")

def setup(bot):
    bot.add_cog(gestion(bot))