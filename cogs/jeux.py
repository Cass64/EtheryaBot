import random
import discord
from discord.ext import commands

class Jeux(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.wallets = {}  # Mini portefeuille en mémoire

    @commands.command()
    async def roll(self, ctx, min_number: int = 1, max_number: int = 100):
        result = random.randint(min_number, max_number)
        await ctx.send(f"🎲 {ctx.author.mention} a tiré {result} entre {min_number} et {max_number}!")

    @commands.command()
    async def dep(self, ctx, amount: int):
        user_id = str(ctx.author.id)
        self.wallets[user_id] = self.wallets.get(user_id, 0) + amount
        await ctx.send(f"💸 {ctx.author.mention} a déposé {amount} coins ! Total: {self.wallets[user_id]} coins.")

    @commands.command()
    async def slut(self, ctx):
        user_id = str(ctx.author.id)
        earnings = random.randint(10, 200)
        self.wallets[user_id] = self.wallets.get(user_id, 0) + earnings
        await ctx.send(f"💋 {ctx.author.mention} a gagné {earnings} coins ! Total: {self.wallets[user_id]} coins.")

async def setup(bot):
    await bot.add_cog(Jeux(bot))
