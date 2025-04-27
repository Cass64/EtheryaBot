import random
import discord
from discord.ext import commands

class Jeux(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.wallets = {}  # Mini portefeuille en mémoire

    @commands.command()
    async def roll(self, ctx, min_number: int = 1, max_number: int = 100):
        """ Lance un dé avec des valeurs entre min_number et max_number. """
        result = random.randint(min_number, max_number)

        embed = discord.Embed(
            title="🎲 Lancer de Dé",
            description=f"{ctx.author.mention} a tiré **{result}** entre **{min_number}** et **{max_number}** !",
            color=discord.Color.blue()  # Couleur bleue pour l'effet ludique
        )
        embed.set_footer(text=f"Commande exécutée par {ctx.author.name}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed)

    @commands.command()
    async def pierre_papier_ciseaux(self, ctx, choix: str):
        """ Joue à Pierre-Papier-Ciseaux avec l'utilisateur. """
        options = ['pierre', 'papier', 'ciseaux']
        choix_utilisateur = choix.lower()
        
        if choix_utilisateur not in options:
            await ctx.send("❌ Choix invalide ! Choisis entre 'pierre', 'papier' ou 'ciseaux'.")
            return

        choix_bot = random.choice(options)
        if choix_utilisateur == choix_bot:
            resultat = "Égalité !"
        elif (choix_utilisateur == "pierre" and choix_bot == "ciseaux") or \
             (choix_utilisateur == "papier" and choix_bot == "pierre") or \
             (choix_utilisateur == "ciseaux" and choix_bot == "papier"):
            resultat = "Tu as gagné !"
        else:
            resultat = "Tu as perdu !"

        embed = discord.Embed(
            title="✂️ Pierre-Papier-Ciseaux",
            description=f"{ctx.author.mention} a choisi **{choix_utilisateur}**.\nLe bot a choisi **{choix_bot}**.\n\n**Résultat**: {resultat}",
            color=discord.Color.green() if "gagné" in resultat else discord.Color.red()
        )
        embed.set_footer(text=f"Commande exécutée par {ctx.author.name}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed)

    @commands.command()
    async def devine_nombre(self, ctx):
        """ Jeu de devinette de nombre entre 1 et 100. """
        number_to_guess = random.randint(1, 100)
        await ctx.send("🕹️ Devine un nombre entre 1 et 100 !")

        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        while True:
            try:
                guess = await self.bot.wait_for('message', check=check, timeout=30.0)
                guess = int(guess.content)

                if guess < number_to_guess:
                    await ctx.send("🔼 Trop bas ! Essaye encore.")
                elif guess > number_to_guess:
                    await ctx.send("🔽 Trop haut ! Essaye encore.")
                else:
                    embed = discord.Embed(
                        title="🎯 Devine le Nombre",
                        description=f"Félicitations {ctx.author.mention} ! Tu as deviné le nombre **{number_to_guess}**.",
                        color=discord.Color.gold()
                    )
                    embed.set_footer(text=f"Commande exécutée par {ctx.author.name}", icon_url=ctx.author.avatar.url)
                    await ctx.send(embed=embed)
                    break

            except ValueError:
                await ctx.send("❌ Ce n'est pas un nombre valide. Essaye encore.")
            except asyncio.TimeoutError:
                await ctx.send("⏳ Temps écoulé ! Tu as mis trop de temps pour deviner.")
                break

# Ajout du cog
async def setup(bot):
    await bot.add_cog(Jeux(bot))
