import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button, Select
from utils.database import get_profiles_collection, get_user_profile, save_user_profile

class Profil(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


async def setup(bot):
    await bot.add_cog(Profil(bot))
