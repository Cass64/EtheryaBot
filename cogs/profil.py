import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button, Select
from utils.database import get_profiles_collection, get_user_profile, save_user_profile


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
        

class ThemeSelect(Select):
    def __init__(self, user_id):
        options = [
            discord.SelectOption(label=theme, description=f"Choisir le thème {theme}", value=theme)
            for theme in THEMES.keys()
        ]
        super().__init__(placeholder="🎨 Choisis ton thème de profil", min_values=1, max_values=1, options=options)
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        if str(interaction.user.id) != str(self.user_id):
            await interaction.response.send_message("❌ Tu ne peux pas modifier le profil d'un autre utilisateur.", ephemeral=True)
            return

        selected_theme = self.values[0]
        color_code = THEMES[selected_theme]

        await save_user_profile(interaction.user.id, {
            "theme": selected_theme,
            "couleur_code": color_code
        })

        await interaction.response.edit_message(content=f"✅ Thème mis à jour : **{selected_theme}**", view=None)


    @app_commands.command(name="myprofil", description="Créer ou modifier ton profil personnel")
    async def myprofil(self, interaction: discord.Interaction,
                       surnom: str = None,
                       photo: str = None,
                       hobby: str = None,
                       aime: str = None,
                       aime_pas: str = None,
                       lieu: str = None,
                       metier: str = None,
                       sexe: str = None,
                       situation: str = None):
        try:
            profil_data = {
                "pseudo": interaction.user.name,
                "surnom": surnom,
                "photo": photo,
                "hobby": hobby,
                "aime": aime,
                "aime_pas": aime_pas,
                "lieu": lieu,
                "metier": metier,
                "sexe": sexe,
                "situation": situation
            }

            await save_user_profile(interaction.user.id, profil_data)

            await interaction.response.send_message(
                "✅ Tes informations de profil ont été enregistrées !",
                ephemeral=True
            )

        except Exception as e:
            print(f"Erreur dans la commande /myprofil pour {interaction.user.id}: {e}")
            await interaction.response.send_message("❌ Une erreur est survenue.", ephemeral=True)

    @app_commands.command(name="profil", description="Voir le profil d'un membre")
    async def profil(self, interaction: discord.Interaction, user: discord.User):
        try:
            profil = await get_user_profile(user.id)

            if not profil:
                await interaction.response.send_message("❌ Ce membre n'a pas encore créé son profil avec /myprofil.", ephemeral=True)
                return

            embed = discord.Embed(
                title=f"📋 Profil de {profil.get('pseudo', 'Inconnu')}",
                description="Voici toutes ses informations 👇",
                color=discord.Color.blue()
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

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            print(f"Erreur dans la commande /profil pour {user.id}: {e}")
            await interaction.response.send_message("❌ Une erreur est survenue.", ephemeral=True)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type == discord.InteractionType.component:
            if interaction.data.get("custom_id", "").startswith("copy_"):
                type_info, text = interaction.data["custom_id"].split(":", 1)
                await interaction.response.send_message(content=f"📝 Voici le texte copié :\n```{text}```", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Profil(bot))
