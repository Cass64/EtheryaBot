import os  
from dotenv import load_dotenv
import discord
from discord import app_commands
from discord.ext import commands, tasks
from keep_alive import keep_alive
import random
import json
import asyncio
import pymongo
from pymongo import MongoClient
from datetime import datetime, timedelta
import math
import aiocron
import logging
import re
import traceback
import time
import subprocess
import sys
from discord.ui import Button, View, Select
from collections import defaultdict, deque
import psutil
import platform
from utils.database import connect_to_mongo

load_dotenv()


MONGO_URI = os.getenv('MONGO_URI')

#CONNEXTION A MONGODB
connect_to_mongo(MONGO_URI)

token = os.getenv('TOKEN_BOT_DISCORD')

# Intents et configuration du bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# Charger les Cogs
initial_extensions = ['cogs.moderation', 'cogs.jeux', 'cogs.gestion']

for extension in initial_extensions:
    bot.load_extension(extension)


@bot.event
async def on_ready():
    print(f'Connecté en tant que {bot.user}!')


keep_alive()
bot.run(token)
