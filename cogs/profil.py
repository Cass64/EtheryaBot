import discord
from discord.ext import commands
from discord import app_commands
from utils.database import get_user_profile, save_user_profile

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
                       situation: str = None,
                       anniversaire: str = None,
                       citation: str = None,
                       reseau_social: str = None,
                       animal_prefere: str = None,
                       couleur: str = None):
        try:
            if couleur and not couleur.startswith("#"):
                couleur = f"#{couleur}"

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
                "situation": situation,
                "anniversaire": anniversaire,
                "citation": citation,
                "reseau_social": reseau_social,
                "animal_prefere": animal_prefere,
                "couleur_code": couleur if couleur else "#3498db"
            }

            await save_user_profile(interaction.user.id, profil_data)

            await interaction.response.send_message(
                "✅ Ton profil a bien été enregistré !",
                ephemeral=True
            )
        except Exception as e:
            print(f"❌ Erreur dans la commande /myprofil pour {interaction.user.id}: {e}")
            await interaction.response.send_message("❌ Une erreur est survenue.", ephemeral=True)

    @app_commands.command(name="profil", description="Voir le profil d'un membre")
    async def profil(self, interaction: discord.Interaction, user: discord.User):
        try:
            profil = await get_user_profile(user.id)

            if not profil:
                await interaction.response.send_message("❌ Ce membre n'a pas encore créé son profil avec /myprofil.", ephemeral=True)
                return

            couleur_code = profil.get("couleur_code", "#3498db")
            color = discord.Color(int(couleur_code.strip("#"), 16))

            embed = discord.Embed(
                description="Voici son profil 👇",
                color=color,
                timestamp=discord.utils.utcnow()
            )

            embed.set_author(name=f"📋 Profil de {profil.get('pseudo', 'Inconnu')}", icon_url=user.display_avatar.url)

            fields = [
                ("📝 Surnom", profil.get("surnom")),
                ("🎯 Hobby", profil.get("hobby")),
                ("💖 Aime", profil.get("aime")),
                ("💔 Aime pas", profil.get("aime_pas")),
                ("📍 Lieu", profil.get("lieu")),
                ("💼 Métier", profil.get("metier")),
                ("⚧️ Sexe", profil.get("sexe")),
                ("💞 Situation amoureuse", profil.get("situation")),
                ("🎂 Anniversaire", profil.get("anniversaire")),
                ("🐾 Animal préféré", profil.get("animal_prefere")),
                ("📜 Citation favorite", profil.get("citation")),
                ("🔗 Réseaux sociaux", profil.get("reseau_social")),
            ]

            for name, value in fields:
                if value:
                    embed.add_field(name=name, value=f"*{value}*", inline=False)

            if profil.get("photo"):
                embed.set_thumbnail(url=profil["photo"])

            embed.set_footer(text=f"Profil généré par {interaction.client.user.name}", icon_url=interaction.client.user.display_avatar.url)

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            print(f"❌ Erreur dans la commande /profil pour {user.id}: {e}")
            await interaction.response.send_message("❌ Une erreur est survenue.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Profil(bot))
