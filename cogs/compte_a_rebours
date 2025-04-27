import discord
from discord.ext import commands
import re

class CompteARebours(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_number = 1  # Le jeu commence à 1
        self.game_active = False  # Vérifier si le jeu est actif
        self.channel_id = 1355230266163204200  # ID du salon spécifique
        self.last_player = None  # Dernier joueur ayant joué

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

        # Vérifier si le message contient un nombre
        if message.content.isdigit():
            num = int(message.content)
            # Si le numéro est correct, réagir avec un "vu"
            if num == self.current_number:
                await message.add_reaction("✅")  # Ajout de la coche verte
                self.current_number += 1
                self.last_player = message.author
                # Pas d'action si c'est correct (le jeu continue)
            else:
                # Si le numéro est incorrect, réagir avec une croix et recommencer
                await message.add_reaction("❌")  # Ajout de la croix rouge
                embed = discord.Embed(
                    title="❌ Jeu terminé",
                    description="Le numéro que tu as écrit est incorrect. Le jeu recommence à **1** !",
                    color=discord.Color.red()
                )
                await message.channel.send(embed=embed)
                self.current_number = 1  # Réinitialiser le jeu
                self.last_player = None
                self.game_active = False  # Terminer le jeu et recommencer à 1

        # Vérifier si le message contient quelque chose d'autre que des chiffres
        elif re.search(r'\D', message.content):
            # Si un autre type de message est envoyé, cela n'est pas comptabilisé comme une victoire ou défaite.
            return

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

        # Vérifier si le message contient un nombre
        if after.content.isdigit():
            num = int(after.content)
            # Si le numéro est correct, réagir avec un "vu"
            if num == self.current_number:
                await after.add_reaction("✅")  # Ajout de la coche verte
                self.current_number += 1
                self.last_player = after.author
            else:
                # Si le numéro est incorrect, réagir avec une croix et recommencer
                await after.add_reaction("❌")  # Ajout de la croix rouge
                embed = discord.Embed(
                    title="❌ Jeu terminé",
                    description="Le numéro que tu as écrit est incorrect. Le jeu recommence à **1** !",
                    color=discord.Color.red()
                )
                await after.channel.send(embed=embed)
                self.current_number = 1  # Réinitialiser le jeu
                self.last_player = None
                self.game_active = False  # Terminer le jeu et recommencer à 1

    @commands.Cog.listener()
    async def on_message(self, message):
        """ Démarrer automatiquement le jeu à partir du numéro 1. """
        if message.channel.id == self.channel_id and not self.game_active:
            self.game_active = True
            await message.channel.send("🎮 Le jeu de compte à rebours commence ! Le premier numéro est **1**. Chaque joueur doit entrer le numéro suivant dans l'ordre.")
            await message.channel.send("Si quelqu'un entre un mauvais numéro ou écrit deux numéros d'affilée, le jeu recommencera à 1.")

# Ajout du cog
async def setup(bot):
    await bot.add_cog(CompteARebours(bot))
