import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Select, View
from utils.database import get_user_profile, save_user_profile

# Liste des couleurs possibles avec des dégradés de fond
COULEURS = {
    "Bleu Ciel": ("#3498db", "#1abc9c"),  # Dégradé Bleu à Vert
    "Rouge Passion": ("#e74c3c", "#c0392b"),  # Dégradé Rouge à Rouge foncé
    "Violet Mystère": ("#9b59b6", "#8e44ad"),  # Dégradé Violet clair à Violet foncé
    "Noir Élégant": ("#2c3e50", "#34495e"),  # Dégradé Noir à Gris
}

class Profil(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    class ThemeSelect(Select):
        def __init__(self, user_id):
            options = [
                discord.SelectOption(label=theme, description=f"Choisir le thème {theme}", value=theme)
                for theme in COULEURS.keys()
            ]
            super().__init__(placeholder="🎨 Choisis ton thème de profil", min_values=1, max_values=1, options=options)
            self.user_id = user_id

        async def callback(self, interaction: discord.Interaction):
            if str(interaction.user.id) != str(self.user_id):
                await interaction.response.send_message("❌ Tu ne peux pas modifier le profil d'un autre utilisateur.", ephemeral=True)
                return

            selected_theme = self.values[0]
            couleur_debut, couleur_fin = COULEURS[selected_theme]

            try:
                # Enregistrer ou modifier les informations du profil avec la couleur choisie
                await save_user_profile(interaction.user.id, {
                    "theme": selected_theme,
                    "couleur_debut": couleur_debut,
                    "couleur_fin": couleur_fin
                })

                await interaction.response.edit_message(content=f"✅ Thème mis à jour : **{selected_theme}**", view=None)
            except Exception as e:
                print(f"❌ Erreur dans le callback ThemeSelect pour {interaction.user.id} : {e}")
                await interaction.response.send_message("❌ Impossible de mettre à jour le thème.", ephemeral=True)

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
                       citation: str = None,
                       anniversaire: str = None,
                       animal_prefere: str = None,
                       couleur: str = None):
        """
        Cette commande permet à un utilisateur de créer ou modifier son profil personnel.
        Les descriptions permettent d'expliquer ce que chaque champ représente.
        """
        try:
            # Descriptions pour chaque option, utilisées dans la commande
            description_fields = {
                "surnom": "Ton surnom ou un autre nom que tes amis utilisent pour t'appeler.",
                "photo": "Lien vers une photo de toi (facultatif).",
                "hobby": "Ton hobby ou activité préférée.",
                "aime": "Les choses que tu aimes.",
                "aime_pas": "Les choses que tu n'aimes pas.",
                "lieu": "Où tu habites.",
                "metier": "Ton métier ou domaine d'activité.",
                "sexe": "Ton sexe (Homme, Femme, Autre).",
                "situation": "Ton état civil actuel.",
                "citation": "Ta citation préférée.",
                "anniversaire": "Ta date d'anniversaire (format: jj/mm).",
                "animal_prefere": "Ton animal préféré.",
            }

            # On vérifie si un profil existe déjà
            profil_data = await get_user_profile(interaction.user.id)
            
            if profil_data:
                # Mettre à jour uniquement les champs modifiés
                for field, value in locals().items():
                    if value is not None and field in description_fields:
                        profil_data[field] = value
            else:
                # Créer un nouveau profil si aucun n'existe
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
                    "animal_prefere": animal_prefere
                }

            # Enregistrer les données du profil avec la couleur sélectionnée
            if couleur:
                profil_data["couleur_debut"], profil_data["couleur_fin"] = COULEURS.get(couleur, ("#3498db", "#1abc9c"))

            await save_user_profile(interaction.user.id, profil_data)

            # Message de confirmation
            await interaction.response.send_message("✅ Tes informations de profil ont été enregistrées ou mises à jour !", ephemeral=True)

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

            couleur_debut = profil.get("couleur_debut", "#3498db")
            couleur_fin = profil.get("couleur_fin", "#1abc9c")
            gradient = f"linear-gradient(45deg, {couleur_debut}, {couleur_fin})"

            embed = discord.Embed(
                description="Voici son profil 👇",
                color=discord.Color.from_rgb(52, 152, 219),  # Fallback color
                timestamp=discord.utils.utcnow()
            )

            embed.set_author(name=f"📋 Profil de {profil.get('pseudo', 'Inconnu')}", icon_url=user.display_avatar.url)

            fields = [
                ("📝 **Surnom**", profil.get("surnom")),
                ("🎯 **Hobby**", profil.get("hobby")),
                ("💖 **Aime**", profil.get("aime")),
                ("💔 **Aime pas**", profil.get("aime_pas")),
                ("📍 **Lieu**", profil.get("lieu")),
                ("💼 **Métier**", profil.get("metier")),
                ("⚧️ **Sexe**", profil.get("sexe")),
                ("💞 **Situation Amoureuse**", profil.get("situation")),
                ("📜 **Citation Favorite**", profil.get("citation")),
                ("🎂 **Anniversaire**", profil.get("anniversaire")),
                ("🐶 **Animal Préféré**", profil.get("animal_prefere"))
            ]

            for name, value in fields:
                if value:
                    embed.add_field(name=name, value=value, inline=False)

            embed.set_thumbnail(url=profil.get("photo", "https://example.com/default-avatar.jpg"))

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            print(f"❌ Erreur dans la commande /profil pour {user.id}: {e}")
            await interaction.response.send_message("❌ Une erreur est survenue.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Profil(bot))
