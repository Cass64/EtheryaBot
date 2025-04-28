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
                       animal_prefere: str = None):
        try:
            profil_data = await get_user_profile(interaction.user.id)

            # Si un profil existe, on met à jour seulement les informations modifiées
            if profil_data:
                if surnom is not None:
                    profil_data["surnom"] = surnom
                if photo is not None:
                    profil_data["photo"] = photo
                if hobby is not None:
                    profil_data["hobby"] = hobby
                if aime is not None:
                    profil_data["aime"] = aime
                if aime_pas is not None:
                    profil_data["aime_pas"] = aime_pas
                if lieu is not None:
                    profil_data["lieu"] = lieu
                if metier is not None:
                    profil_data["metier"] = metier
                if sexe is not None:
                    profil_data["sexe"] = sexe
                if situation is not None:
                    profil_data["situation"] = situation
                if citation is not None:
                    profil_data["citation"] = citation
                if anniversaire is not None:
                    profil_data["anniversaire"] = anniversaire
                if animal_prefere is not None:
                    profil_data["animal_prefere"] = animal_prefere
            else:
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

            await save_user_profile(interaction.user.id, profil_data)

            # Créer un menu déroulant pour choisir la couleur
            theme_select = self.ThemeSelect(interaction.user.id)
            view = View()
            view.add_item(theme_select)

            await interaction.response.send_message(
                "✅ Tes informations de profil ont été enregistrées ou mises à jour ! Choisis un thème de couleur pour ton profil.",
                view=view, ephemeral=True
            )

        except Exception as e:
            print(f"❌ Erreur dans la commande /myprofil pour {interaction.user.id}: {e}")
            await interaction.response.send_message("❌ Une erreur est survenue.", ephemeral=True)

    @app_commands.command(name="profil", description="Voir le profil d'un membre")
    async def profil(self, interaction: discord.Interaction, user: discord.User = None):
        try:
            # Si l'utilisateur ne mentionne personne, on lui montre son propre profil
            if user is None:
                user = interaction.user

            profil = await get_user_profile(user.id)

            if not profil:
                await interaction.response.send_message("❌ Ce membre n'a pas encore créé son profil avec /myprofil.", ephemeral=True)
                return

            # Récupérer les couleurs du profil, ou utiliser des couleurs par défaut si non renseignées
            couleur_debut = profil.get("couleur_debut", "#3498db")
            couleur_fin = profil.get("couleur_fin", "#1abc9c")
            gradient = f"linear-gradient(45deg, {couleur_debut}, {couleur_fin})"

            embed = discord.Embed(
                description="Voici son profil 👇",
                color=discord.Color.from_rgb(52, 152, 219),  # Fallback color
                timestamp=discord.utils.utcnow()
            )

            # Appliquer le dégradé de couleurs à l'embed (dans le champ "description")
            embed.description = f"[Profil de {user.name}]({user.display_avatar.url}) - Thème : {profil.get('theme', 'Non défini')}"

            # Bannière personnalisée (image de fond)
            embed.set_image(url="https://github.com/Cass64/EtheryaBot/blob/main/images_etherya/banniere_profil.png?raw=true")

            # Avatar circulaire avec bordure
            embed.set_author(name=f"📋 Profil de {profil.get('pseudo', 'Inconnu')}", icon_url=user.display_avatar.url)

            # Disposition améliorée des informations avec colonnes
            fields = [
                ("📝 **Surnom**", profil.get("surnom", "Non renseigné")),
                ("🎯 **Hobby**", profil.get("hobby", "Non renseigné")),
                ("💖 **Aime**", profil.get("aime", "Non renseigné")),
                ("💔 **Aime pas**", profil.get("aime_pas", "Non renseigné")),
                ("📍 **Lieu**", profil.get("lieu", "Non renseigné")),
                ("💼 **Métier**", profil.get("metier", "Non renseigné")),
                ("⚧️ **Sexe**", profil.get("sexe", "Non renseigné")),
                ("💞 **Situation Amoureuse**", profil.get("situation", "Non renseigné")),
                ("📜 **Citation Favorite**", profil.get("citation", "Non renseigné")),
                ("🎂 **Anniversaire**", profil.get("anniversaire", "Non renseigné")),
                ("🐶 **Animal Préféré**", profil.get("animal_prefere", "Non renseigné"))
            ]

            # Répartir les champs en deux colonnes
            inline = True
            for i, (name, value) in enumerate(fields):
                if value != "Non renseigné":  # Seulement afficher les champs renseignés
                    embed.add_field(name=name, value=f"**{value}**", inline=inline)
                    inline = not inline  # Alterne entre True et False pour la disposition en colonnes

            # Footer et Image d'avatar
            embed.set_footer(text=f"Profil généré par {interaction.client.user.name}", icon_url=interaction.client.user.display_avatar.url)
            embed.set_thumbnail(url=profil.get("photo", "https://example.com/default-avatar.jpg"))

            # Appliquer le dégradé de couleurs comme fond
            embed.color = discord.Color.from_rgb(int(couleur_debut[1:3], 16), int(couleur_debut[3:5], 16), int(couleur_debut[5:7], 16))

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            print(f"❌ Erreur dans la commande /profil pour {user.id}: {e}")
            await interaction.response.send_message("❌ Une erreur est survenue.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Profil(bot))
