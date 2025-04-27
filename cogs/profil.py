import discord
from discord.ext import commands
from discord import app_commands
from utils.database import get_user_profile, save_user_profile

class Profil(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="myprofil", description="Crée ou modifie ton profil personnel.")
    async def myprofil(self, interaction: discord.Interaction):
        await interaction.response.send_modal(MyProfilModal())

    @app_commands.command(name="profil", description="Voir le profil d'un utilisateur.")
    @app_commands.describe(user="L'utilisateur dont tu veux voir le profil")
    async def profil(self, interaction: discord.Interaction, user: discord.User = None):
        user = user or interaction.user  # Si personne n'est précisé, montrer son propre profil

        profil_data = get_user_profile(user.id)
        if not profil_data:
            await interaction.response.send_message(f"❌ {user.mention} n'a pas encore créé son profil avec `/myprofil`.", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"🎨 Profil de {user.name}",
            description=f"Voici les informations de **{user.mention}**",
            color=int(profil_data.get("color", "0x00BFFF"), 16)  # Couleur personnalisée ou bleu par défaut
        )
        embed.set_thumbnail(url=profil_data.get("photo") or user.display_avatar.url)

        # Ajout des champs si présents
        if profil_data.get("surnom"):
            embed.add_field(name="🎭 Surnom", value=profil_data["surnom"], inline=False)
        if profil_data.get("hobby"):
            embed.add_field(name="🎯 Hobby", value=profil_data["hobby"], inline=False)
        if profil_data.get("aime"):
            embed.add_field(name="💖 Aime", value=profil_data["aime"], inline=False)
        if profil_data.get("aime_pas"):
            embed.add_field(name="💔 N'aime pas", value=profil_data["aime_pas"], inline=False)
        if profil_data.get("lieu"):
            embed.add_field(name="🏠 Lieu", value=profil_data["lieu"], inline=False)
        if profil_data.get("job"):
            embed.add_field(name="🛠️ Fait quoi ?", value=profil_data["job"], inline=False)
        if profil_data.get("sexe"):
            embed.add_field(name="⚧️ Sexe", value=profil_data["sexe"], inline=False)
        if profil_data.get("situation"):
            embed.add_field(name="💌 Situation amoureuse", value=profil_data["situation"], inline=False)

        await interaction.response.send_message(embed=embed)

# Le Modal (formulaire) pour remplir son profil
class MyProfilModal(discord.ui.Modal, title="📝 Mon Profil"):

    surnom = discord.ui.TextInput(label="🎭 Ton surnom", required=False, max_length=100)
    photo = discord.ui.TextInput(label="🖼️ Lien d'une image de profil", required=False)
    hobby = discord.ui.TextInput(label="🎯 Tes hobbies", required=False, max_length=200)
    aime = discord.ui.TextInput(label="💖 Ce que tu aimes", required=False, max_length=200)
    aime_pas = discord.ui.TextInput(label="💔 Ce que tu n'aimes pas", required=False, max_length=200)
    lieu = discord.ui.TextInput(label="🏠 Où tu habites", required=False, max_length=100)
    job = discord.ui.TextInput(label="🛠️ Ton métier/activité", required=False, max_length=100)
    sexe = discord.ui.TextInput(label="⚧️ Ton sexe", required=False, max_length=20)
    situation = discord.ui.TextInput(label="💌 Situation amoureuse", required=False, max_length=100)
    color = discord.ui.TextInput(label="🎨 Couleur d'embed (ex: 0x3498DB)", required=False, default="0x00BFFF")

    async def on_submit(self, interaction: discord.Interaction):
        data = {
            "surnom": self.surnom.value,
            "photo": self.photo.value,
            "hobby": self.hobby.value,
            "aime": self.aime.value,
            "aime_pas": self.aime_pas.value,
            "lieu": self.lieu.value,
            "job": self.job.value,
            "sexe": self.sexe.value,
            "situation": self.situation.value,
            "color": self.color.value
        }
        save_user_profile(interaction.user.id, data)
        await interaction.response.send_message("✅ Ton profil a bien été enregistré/édité !", ephemeral=True)

# Ajout du Cog
async def setup(bot):
    await bot.add_cog(Profil(bot))
