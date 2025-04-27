import discord
from discord.ext import commands
import random

class Jeux(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="roll")
    async def roll(self, ctx):
        """Lance un dé et donne un chiffre aléatoire entre 1 et 6"""
        number = random.randint(1, 6)
        await ctx.send(f"🎲 Tu as lancé un {number} !")

async def setup(bot):
    await bot.add_cog(Jeux(bot))
