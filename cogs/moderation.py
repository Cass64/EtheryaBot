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
        await member.ban(reason=reason)
        await ctx.send(f"🔨 {member} a été banni. Raison : {reason}")

    @commands.command()
    @commands.check(is_mod)  # Vérification de rôle
    async def kick(self, ctx, member: discord.Member, *, reason="Aucune raison"):
        await member.kick(reason=reason)
        await ctx.send(f"👢 {member} a été kick. Raison : {reason}")

    @commands.command()
    @commands.check(is_mod)  # Vérification de rôle
    async def warn(self, ctx, member: discord.Member, *, reason="Aucune raison"):
        await ctx.send(f"⚠️ {member.mention} a été warn. Raison : {reason}")

# Ajout du cog
async def setup(bot):
    await bot.add_cog(Moderation(bot))
