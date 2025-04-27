from discord.ext import commands
import random

class Jeux(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='roll')
    async def roll(self, ctx, min: int = 1, max: int = 6):
        """Lance un dé."""
        result = random.randint(min, max)
        await ctx.send(f'🎲 {ctx.author.mention} a lancé le dé et a obtenu : **{result}** !')

def setup(bot):
    bot.add_cog(Jeux(bot))
