import discord
from discord.ext import commands
import re

class CompteARebours(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_number = 1  # Le jeu commence à 1
        self.game_active = True  # Le jeu est toujours actif
        self.channel_id = 1355230266163204200  # ID du salon spécifique

    @commands.Cog.listener()
    async def on_message(self, message):
        """ Fonction pour gérer les messages dans le salon spécifique. """
        if message.author.bot:
            return

        if message.channel.id != self.channel_id:
            return  # Si le message n'est pas dans le salon spécifié, on l'ignore

        # Vérifier si le jeu est actif
        if not self.game_active:
            return

        # Vérifier si le message contient un nombre entier et seulement un nombre
        if message.content.isdigit():
            num = int(message.content)

            # Si le numéro est correct
            if num == self.current_number:
                await message.add_reaction("✅")  # Ajout de la coche verte
                self.current_number += 1  # Passer au numéro suivant
            else:
                # Si le numéro est incorrect, réagir avec une croix et recommencer à 1
                await message.add_reaction("❌")  # Ajout de la croix rouge
                embed = discord.Embed(
                    title="❌ Jeu terminé",
                    description="Le numéro que tu as écrit est incorrect. Le jeu recommence à **1** !",
                    color=discord.Color.red()
                )
                await message.channel.send(embed=embed)
                self.current_number = 1  # Réinitialiser le jeu à 1

        # Vérifier si le message contient un autre type de texte (pas un numéro seul)
        elif re.search(r'\D', message.content):
            return  # Si ce n'est pas un nombre, ne rien faire et continuer

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        """ Fonction pour vérifier les messages édités dans le salon spécifique. """
        # Répéter le même comportement que pour les nouveaux messages
        if after.author.bot:
            return

        if after.channel.id != self.channel_id:
            return  # Si le message n'est pas dans le salon spécifié, on l'ignore

        # Vérifier si le jeu est actif
        if not self.game_active:
            return

        # Vérifier si le message contient un nombre entier
        if after.content.isdigit():
            num = int(after.content)

            # Si le numéro est correct
            if num == self.current_number:
                await after.add_reaction("✅")  # Ajout de la coche verte
                self.current_number += 1  # Passer au numéro suivant
            else:
                # Si le numéro est incorrect, réagir avec une croix et recommencer à 1
                await after.add_reaction("❌")  # Ajout de la croix rouge
                embed = discord.Embed(
                    title="❌ Jeu terminé",
                    description="Le numéro que tu as écrit est incorrect. Le jeu recommence à **1** !",
                    color=discord.Color.red()
                )
                await after.channel.send(embed=embed)
                self.current_number = 1  # Réinitialiser le jeu à 1

    @commands.Cog.listener()
    async def on_message(self, message):
        """ Fonction pour démarrer le jeu sans message. Le jeu est continu, pas besoin de redémarrage manuel. """
        if message.channel.id == self.channel_id:
            return  # Le jeu commence automatiquement, pas besoin de message de démarrage

# Ajout du cog
async def setup(bot):
    await bot.add_cog(CompteARebours(bot))
