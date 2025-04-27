import discord
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Vérification du rôle avant d'exécuter la commande
    def is_mod(ctx):
        role_id = 1287445477364727930  # L'ID du rôle requis
        return any(role.id == role_id for role in ctx.author.roles)

    @commands.command()
    @commands.check(is_mod)  # Vérification de rôle
    async def ban(self, ctx, member: discord.Member, *, reason="Aucune raison"):
        embed = discord.Embed(
            title="Bannissement",
            description=f"{member.mention} a été banni.",
            color=discord.Color.red()  # Rouge pour bannissement
        )
        embed.add_field(name="Raison", value=reason, inline=False)
        embed.set_footer(text=f"Commande exécutée par {ctx.author.name}", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.check(is_mod)  # Vérification de rôle
    async def kick(self, ctx, member: discord.Member, *, reason="Aucune raison"):
        embed = discord.Embed(
            title="Expulsion",
            description=f"{member.mention} a été expulsé.",
            color=discord.Color.orange()  # Orange pour expulsion
        )
        embed.add_field(name="Raison", value=reason, inline=False)
        embed.set_footer(text=f"Commande exécutée par {ctx.author.name}", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.check(is_mod)  # Vérification de rôle
    async def warn(self, ctx, member: discord.Member, *, reason="Aucune raison"):
        embed = discord.Embed(
            title="Avertissement",
            description=f"{member.mention} a reçu un avertissement.",
            color=discord.Color.gold()  # Or pour un avertissement
        )
        embed.add_field(name="Raison", value=reason, inline=False)
        embed.set_footer(text=f"Commande exécutée par {ctx.author.name}", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

# Ajout du cog
async def setup(bot):
    await bot.add_cog(Moderation(bot))
