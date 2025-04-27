import discord
from discord.ext import commands
from discord import app_commands
from utils.database import db  # J'imagine que db = ta connexion MongoDB
import re

class Profil(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.collection = db["profils"]  # Collection MongoDB

    @app_commands.command(name="myprofil", description="Créer ou modifier ton profil personnel")
    @app_commands.describe(
        surnom="Ton surnom (facultatif)",
        photo="Lien de ta photo (facultatif)",
        hobby="Tes hobbies (facultatif)",
        aime="Ce que tu aimes (facultatif)",
        aime_pas="Ce que tu n'aimes pas (facultatif)",
        lieu="Où tu habites (facultatif)",
        travail="Que fais-tu dans la vie (facultatif)",
        sexe="Ton genre (facultatif)",
        situation="Ta situation amoureuse (facultatif)",
        couleur="Couleur de ton profil en hex (#00FF00 par exemple, facultatif)"
    )
    async def myprofil(
        self, interaction: discord.Interaction,
        surnom: str = None,
        photo: str = None,
        hobby: str = None,
        aime: str = None,
        aime_pas: str = None,
        lieu: str = None,
        travail: str = None,
        sexe: str = None,
        situation: str = None,
        couleur: str = None
    ):
        await interaction.response.defer(thinking=True)

        # Vérification de la couleur
        color_value = discord.Color.blurple()
        if couleur:
            if re.match(r"^#([A-Fa-f0-9]{6})$", couleur):
                color_value = discord.Color(int(couleur[1:], 16))
            else:
                await interaction.followup.send("❌ La couleur doit être au format hexadécimal (ex: `#FF0000`).", ephemeral=True)
                return

        profil_data = {
            "user_id": interaction.user.id,
            "pseudo": interaction.user.name,
            "surnom": surnom,
            "photo": photo,
            "hobby": hobby,
            "aime": aime,
            "aime_pas": aime_pas,
            "lieu": lieu,
            "travail": travail,
            "sexe": sexe,
            "situation": situation,
            "couleur": couleur
        }

        # Mettre à jour ou créer le profil
        self.collection.update_one(
            {"user_id": interaction.user.id},
            {"$set": profil_data},
            upsert=True
        )

        await interaction.followup.send("✅ Ton profil a bien été enregistré ou modifié !", ephemeral=True)

    @app_commands.command(name="profil", description="Voir le profil d'un utilisateur")
    @app_commands.describe(user="L'utilisateur dont tu veux voir le profil")
    async def profil(self, interaction: discord.Interaction, user: discord.User):
        await interaction.response.defer(thinking=True)

        profil = self.collection.find_one({"user_id": user.id})
        if not profil:
            await interaction.followup.send("❌ Ce membre n'a pas encore créé son profil avec `/myprofil`.", ephemeral=True)
            return

        # Utiliser la couleur personnalisée ou une couleur par défaut
        embed_color = discord.Color.blurple()
        if profil.get("couleur") and re.match(r"^#([A-Fa-f0-9]{6})$", profil["couleur"]):
            embed_color = discord.Color(int(profil["couleur"][1:], 16))

        embed = discord.Embed(
            title=f"Profil de {profil['pseudo']}",
            color=embed_color
        )

        if profil.get("surnom"):
            embed.add_field(name="Surnom", value=profil["surnom"], inline=False)
        if profil.get("hobby"):
            embed.add_field(name="Hobbies", value=profil["hobby"], inline=False)
        if profil.get("aime"):
            embed.add_field(name="Aime", value=profil["aime"], inline=False)
        if profil.get("aime_pas"):
            embed.add_field(name="N'aime pas", value=profil["aime_pas"], inline=False)
        if profil.get("lieu"):
            embed.add_field(name="Lieu", value=profil["lieu"], inline=False)
        if profil.get("travail"):
            embed.add_field(name="Travail", value=profil["travail"], inline=False)
        if profil.get("sexe"):
            embed.add_field(name="Sexe", value=profil["sexe"], inline=False)
        if profil.get("situation"):
            embed.add_field(name="Situation Amoureuse", value=profil["situation"], inline=False)

        if profil.get("photo"):
            embed.set_thumbnail(url=profil["photo"])

        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Profil(bot))
