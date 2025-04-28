import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
from utils.database import get_profiles_collection

# Thèmes disponibles
THEMES = {
    "Bleu Ciel": "#3498db",
    "Vert Forêt": "#2ecc71",
    "Rouge Passion": "#e74c3c",
    "Violet Mystère": "#9b59b6",
    "Noir Élégant": "#2c3e50"
}

class Profil(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        # Ajouter les commandes à l'arbre du bot
        self.bot.tree.add_command(self.myprofil)
        self.bot.tree.add_command(self.profil)

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
        theme="Choisir un thème de couleur"
    )
    @app_commands.choices(theme=[
        app_commands.Choice(name="Bleu Ciel", value="Bleu Ciel"),
        app_commands.Choice(name="Vert Forêt", value="Vert Forêt"),
        app_commands.Choice(name="Rouge Passion", value="Rouge Passion"),
        app_commands.Choice(name="Violet Mystère", value="Violet Mystère"),
        app_commands.Choice(name="Noir Élégant", value="Noir Élégant"),
    ])
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
                       theme: app_commands.Choice[str] = None):
        """Créer ou modifier son profil utilisateur."""

        try:
            user_id = str(interaction.user.id)
            selected_theme = theme.value if theme else None
            color_code = THEMES.get(selected_theme, None)

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
                "theme": selected_theme,
                "couleur_code": color_code
            }

            await get_profiles_collection().update_one(
                {"user_id": user_id},
                {"$set": profil_data},
                upsert=True
            )

            await interaction.response.send_message("✅ Ton profil a été enregistré/modifié avec succès !", ephemeral=True)

        except Exception as e:
            print(f"Erreur dans la commande /myprofil pour {interaction.user.id}: {e}")
            await interaction.response.send_message("❌ Une erreur s'est produite lors de l'enregistrement de ton profil.", ephemeral=True)

    @app_commands.command(name="profil", description="Voir le profil d'un membre")
    @app_commands.describe(user="Choisis un membre")
    async def profil(self, interaction: discord.Interaction, user: discord.User):
        """Afficher le profil d'un utilisateur."""

        try:
            user_id = str(user.id)
            profil = await get_profiles_collection().find_one({"user_id": user_id})

            if not profil:
                await interaction.response.send_message("❌ Ce membre n'a pas encore créé son profil avec /myprofil.", ephemeral=True)
                return

            color = discord.Color.blue()
            if profil.get("couleur_code"):
                try:
                    color = discord.Color(int(profil["couleur_code"].replace("#", ""), 16))
                except Exception:
                    pass

            embed = discord.Embed(
                title=f"📋 Profil de {profil['pseudo']}",
                description="Voici toutes ses informations personnelles 👇",
                color=color
            )

            fields = [
                ("📝 Surnom", profil.get("surnom")),
                ("🎯 Hobby", profil.get("hobby")),
                ("💖 Aime", profil.get("aime")),
                ("💔 Aime pas", profil.get("aime_pas")),
                ("📍 Lieu", profil.get("lieu")),
                ("💼 Métier", profil.get("metier")),
                ("⚧️ Sexe", profil.get("sexe")),
                ("💞 Situation Amoureuse", profil.get("situation"))
            ]

            for name, value in fields:
                if value:
                    embed.add_field(name=name, value=value, inline=False)

            if profil.get("photo"):
                embed.set_thumbnail(url=profil["photo"])

            view = View()

            # Ajouter des boutons pour copier certaines infos
            if profil.get("hobby"):
                view.add_item(Button(label="📋 Copier Hobby", style=discord.ButtonStyle.primary, custom_id=f"copy_hobby:{profil['hobby']}"))
            if profil.get("aime"):
                view.add_item(Button(label="📋 Copier Aime", style=discord.ButtonStyle.success, custom_id=f"copy_aime:{profil['aime']}"))
            if profil.get("aime_pas"):
                view.add_item(Button(label="📋 Copier Aime Pas", style=discord.ButtonStyle.danger, custom_id=f"copy_aime_pas:{profil['aime_pas']}"))

            await interaction.response.send_message(embed=embed, view=view)

        except Exception as e:
            print(f"Erreur dans la commande /profil pour {user.id}: {e}")
            await interaction.response.send_message("❌ Une erreur s'est produite lors de l'affichage du profil.", ephemeral=True)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type == discord.InteractionType.component:
            if interaction.data["custom_id"].startswith("copy_"):
                type_info, text = interaction.data["custom_id"].split(":", 1)
                await interaction.response.send_message(content=f"📝 Voici le texte copié :\n```{text}```", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Profil(bot))
