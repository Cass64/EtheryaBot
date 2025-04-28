import discord
from discord.ext import commands
from discord import app_commands
from typing import Literal
from utils.database import get_user_profile, save_user_profile

# Liste des couleurs disponibles
COULEURS = {
    "Bleu Ciel": ("#3498db", "#1abc9c"),
    "Rouge Passion": ("#e74c3c", "#c0392b"),
    "Violet Mystère": ("#9b59b6", "#8e44ad"),
    "Noir Élégant": ("#2c3e50", "#34495e"),
    "Vert Nature": ("#2ecc71", "#27ae60"),
}

class Profil(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Fonction d'autocomplete pour le choix des couleurs
    async def couleur_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> list[app_commands.Choice[str]]:
        couleurs_disponibles = []
        for couleur in COULEURS.keys():
            if current.lower() in couleur.lower():
                couleurs_disponibles.append(app_commands.Choice(name=couleur, value=couleur))
        return couleurs_disponibles[:25]  # Discord limite à 25 choix max

    @app_commands.command(name="myprofil", description="Créer ou modifier ton profil personnel")
    @app_commands.describe(
        surnom="Ton surnom ou pseudo",
        photo="Lien d'une photo pour ton profil",
        hobby="Ton activité préférée",
        aime="Ce que tu aimes dans la vie",
        aime_pas="Ce que tu n'aimes pas du tout",
        lieu="Où tu habites",
        metier="Ton métier actuel",
        sexe="Ton sexe (homme, femme, autre)",
        situation="Ta situation amoureuse",
        citation="Ta citation préférée",
        anniversaire="Ton anniversaire (JJ/MM)",
        animal_prefere="Ton animal préféré",
        couleur="Choisis ton thème de couleur pour ton profil"
    )
    @app_commands.autocomplete(couleur=couleur_autocomplete)
    async def myprofil(self, interaction: discord.Interaction,
                       surnom: str,
                       photo: str,
                       hobby: str,
                       aime: str,
                       aime_pas: str,
                       lieu: str,
                       metier: str,
                       sexe: str,
                       situation: str,
                       citation: str,
                       anniversaire: str,
                       animal_prefere: str,
                       couleur: str):
        """Créer ou mettre à jour ton profil personnel."""
        try:
            couleur_debut, couleur_fin = COULEURS.get(couleur, ("#3498db", "#1abc9c"))

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
                "citation": citation,
                "anniversaire": anniversaire,
                "animal_prefere": animal_prefere,
                "theme": couleur,
                "couleur_debut": couleur_debut,
                "couleur_fin": couleur_fin
            }

            await save_user_profile(interaction.user.id, profil_data)

            await interaction.response.send_message(
                "✅ Ton profil a été enregistré ou mis à jour avec succès !",
                ephemeral=True
            )

        except Exception as e:
            print(f"❌ Erreur dans /myprofil : {e}")
            await interaction.response.send_message("❌ Une erreur est survenue.", ephemeral=True)

    @app_commands.command(name="profil", description="Voir le profil d'un membre")
    @app_commands.describe(
        user="Le membre dont tu veux voir le profil"
    )
    async def profil(self, interaction: discord.Interaction, user: discord.User):
        """Voir le profil d'un utilisateur."""
        try:
            profil = await get_user_profile(user.id)

            if not profil:
                await interaction.response.send_message(
                    "❌ Ce membre n'a pas encore créé son profil avec /myprofil.",
                    ephemeral=True
                )
                return

            couleur_debut = profil.get("couleur_debut", "#3498db")
            couleur_fin = profil.get("couleur_fin", "#1abc9c")

            embed = discord.Embed(
                description="Voici son profil 👇",
                color=discord.Color.from_str(couleur_debut),
                timestamp=discord.utils.utcnow()
            )

            embed.set_author(name=f"📋 Profil de {profil.get('pseudo', 'Inconnu')}", icon_url=user.display_avatar.url)
            embed.set_thumbnail(url=profil.get("photo", "https://example.com/default-avatar.jpg"))
            embed.set_image(url="https://github.com/Cass64/EtheryaBot/blob/main/images_etherya/banniere_profil.png?raw=true")  # à remplacer par ton image bannière par défaut

            champs = [
                ("📝 Surnom", profil.get("surnom")),
                ("🎯 Hobby", profil.get("hobby")),
                ("💖 Aime", profil.get("aime")),
                ("💔 Aime pas", profil.get("aime_pas")),
                ("📍 Lieu", profil.get("lieu")),
                ("💼 Métier", profil.get("metier")),
                ("⚧️ Sexe", profil.get("sexe")),
                ("💞 Situation", profil.get("situation")),
                ("📜 Citation", profil.get("citation")),
                ("🎂 Anniversaire", profil.get("anniversaire")),
                ("🐶 Animal Préféré", profil.get("animal_prefere")),
            ]

            for titre, valeur in champs:
                if valeur:
                    embed.add_field(name=titre, value=valeur, inline=False)

            embed.set_footer(text=f"Profil généré par {interaction.client.user.name}", icon_url=interaction.client.user.display_avatar.url)

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            print(f"❌ Erreur dans /profil : {e}")
            await interaction.response.send_message("❌ Une erreur est survenue.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Profil(bot))
