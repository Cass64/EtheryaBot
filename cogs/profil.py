import discord
from discord.ext import commands
from discord import app_commands
from utils.database import db
from discord.ui import View, Button

class Profil(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="myprofil", description="Créer ou modifier ton profil personnel")
    @app_commands.describe(
        surnom="Ton surnom",
        photo="Lien URL de ta photo",
        hobby="Tes hobbies",
        aime="Ce que tu aimes",
        aime_pas="Ce que tu n'aimes pas",
        lieu="Où tu habites",
        metier="Ton métier ou activité",
        sexe="Ton sexe",
        situation="Ta situation amoureuse",
        couleur_embed="Couleur de ton profil (ex: #00FF00)"
    )
    async def myprofil(self, interaction: discord.Interaction,
                       surnom: str = None,
                       photo: str = None,
                       hobby: str = None,
                       aime: str = None,
                       aime_pas: str = None,
                       lieu: str = None,
                       metier: str = None,
                       sexe: str = None,
                       situation: str = None,
                       couleur_embed: str = None):

        user_id = str(interaction.user.id)

        profil_data = {
            "user_id": user_id,
            "pseudo": interaction.user.name,
            "surnom": surnom,
            "photo": photo,
            "hobby": hobby,
            "aime": aime,
            "aime_pas": aime_pas,
            "lieu": lieu,
            "metier": metier,
            "sexe": sexe,
            "situation": situation,
            "couleur_embed": couleur_embed
        }

        await db["profils"].update_one(
            {"user_id": user_id},
            {"$set": profil_data},
            upsert=True
        )

        await interaction.response.send_message("✅ Ton profil a été enregistré/modifié avec succès !", ephemeral=True)

    @app_commands.command(name="profil", description="Voir le profil d'un membre")
    @app_commands.describe(user="Choisis un membre")
    async def profil(self, interaction: discord.Interaction, user: discord.User):

        user_id = str(user.id)

        profil = await db["profils"].find_one({"user_id": user_id})

        if not profil:
            await interaction.response.send_message("❌ Ce membre n'a pas encore créé son profil avec /myprofil.", ephemeral=True)
            return

        color = discord.Color.blue()
        if profil.get("couleur_embed"):
            try:
                color = discord.Color(int(profil["couleur_embed"].replace("#", ""), 16))
            except Exception:
                pass

        embed = discord.Embed(
            title=f"📋 Profil de {profil['pseudo']}",
            description="Voici toutes ses informations personnelles 👇",
            color=color
        )

        if profil.get("surnom"):
            embed.add_field(name="📝 Surnom", value=profil["surnom"], inline=False)
        if profil.get("hobby"):
            embed.add_field(name="🎯 Hobby", value=profil["hobby"], inline=False)
        if profil.get("aime"):
            embed.add_field(name="💖 Aime", value=profil["aime"], inline=False)
        if profil.get("aime_pas"):
            embed.add_field(name="💔 Aime pas", value=profil["aime_pas"], inline=False)
        if profil.get("lieu"):
            embed.add_field(name="📍 Lieu", value=profil["lieu"], inline=False)
        if profil.get("metier"):
            embed.add_field(name="💼 Métier", value=profil["metier"], inline=False)
        if profil.get("sexe"):
            embed.add_field(name="⚧️ Sexe", value=profil["sexe"], inline=True)
        if profil.get("situation"):
            embed.add_field(name="💞 Situation Amoureuse", value=profil["situation"], inline=True)

        if profil.get("photo"):
            embed.set_thumbnail(url=profil["photo"])

        view = View()

        if profil.get("hobby"):
            view.add_item(Button(label="📋 Copier Hobby", style=discord.ButtonStyle.primary, custom_id=f"copy_hobby:{profil['hobby']}"))
        if profil.get("aime"):
            view.add_item(Button(label="📋 Copier Aime", style=discord.ButtonStyle.success, custom_id=f"copy_aime:{profil['aime']}"))
        if profil.get("aime_pas"):
            view.add_item(Button(label="📋 Copier Aime Pas", style=discord.ButtonStyle.danger, custom_id=f"copy_aime_pas:{profil['aime_pas']}"))

        await interaction.response.send_message(embed=embed, view=view)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type == discord.InteractionType.component:
            if interaction.data["custom_id"].startswith("copy_"):
                type_info, text = interaction.data["custom_id"].split(":", 1)
                await interaction.response.send_message(content=f"📝 Voici le texte copié :\n```{text}```", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Profil(bot))
