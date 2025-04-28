import discord
from discord.ext import commands
from discord import app_commands

class Gestion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="clear", description="Supprime un certain nombre de messages dans le canal.")
    @app_commands.describe(nombre="Nombre de messages à supprimer")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, nombre: int):
        """Supprime un nombre de messages spécifié dans le salon."""
        try:
            if nombre <= 0:
                await interaction.response.send_message("Le nombre de messages à supprimer doit être supérieur à zéro.", ephemeral=True)
                return

            await interaction.response.defer(ephemeral=True)  # Répond en différé avant de supprimer
            deleted = await interaction.channel.purge(limit=nombre)

            await interaction.followup.send(f"✅ {len(deleted)} messages ont été supprimés.", ephemeral=True)

        except Exception as e:
            print(f"Erreur dans la commande /clear : {e}")
            await interaction.followup.send("❌ Une erreur est survenue lors de la suppression.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Gestion(bot))
