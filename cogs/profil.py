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
    async def myprofil(self, interaction: discord.Interaction):
        try:
            # Guide utilisateur avec des descriptions des champs à remplir
            description_fields = {
                "Surnom": "Ton surnom ou un autre nom que tes amis utilisent pour t'appeler.",
                "Photo": "Lien vers une photo de toi (facultatif).",
                "Hobby": "Ton hobby ou activité préférée.",
                "Aime": "Les choses que tu aimes.",
                "Aime Pas": "Les choses que tu n'aimes pas.",
                "Lieu": "Où tu habites.",
                "Métier": "Ton métier ou domaine d'activité.",
                "Sexe": "Ton sexe (Homme, Femme, Autre).",
                "Situation Amoureuse": "Ton état civil actuel.",
                "Citation Favorite": "Ta citation préférée.",
                "Anniversaire": "Ta date d'anniversaire (format: jj/mm).",
                "Animal Préféré": "Ton animal préféré.",
            }

            # Envoi des descriptions des champs pour guider l'utilisateur
            for field, description in description_fields.items():
                await interaction.response.send_message(f"**{field}** : {description}", ephemeral=True)

            # Demande d'informations à l'utilisateur
            await interaction.response.send_message("💬 Veuillez remplir les informations ci-dessus. Si vous ne souhaitez pas remplir un champ, laissez-le vide.", ephemeral=True)

            # Sélection de la couleur de l'embed via un menu déroulant
            color_select = self.ThemeSelect(user_id=interaction.user.id)
            view = View()
            view.add_item(color_select)
            await interaction.response.send_message("🎨 Choisis une couleur pour ton profil", view=view, ephemeral=True)

            # Attendre la réponse de l'utilisateur
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
