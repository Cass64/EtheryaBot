import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Select, View
from utils.database import get_user_profile, save_user_profile
import re  # Pour utiliser la validation du format de la date
from datetime import datetime
import traceback


# Fonction de validation du format d'anniversaire
def validate_birthday(birthday: str) -> bool:
    """Valide si la date de naissance est au format DD/MM/YYYY."""
    pattern = r"^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d{4}$"
    return re.match(pattern, birthday) is not None

COULEURS = {
    "Bleu Ciel": ("#3498db", "#1abc9c"),
    "Rouge Passion": ("#e74c3c", "#c0392b"),
    "Violet Mystère": ("#9b59b6", "#8e44ad"),
    "Noir Élégant": ("#2c3e50", "#34495e"),
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
                profil = await get_user_profile(interaction.user.id)
                profil["theme"] = selected_theme
                profil["couleur_debut"] = couleur_debut
                profil["couleur_fin"] = couleur_fin
                await save_user_profile(interaction.user.id, profil)

                await interaction.response.edit_message(
                    content=f"✅ Thème mis à jour : **{selected_theme}**",
                    embed=None,
                    view=None
                )
            except Exception as e:
                print(f"❌ Erreur ThemeSelect pour {interaction.user.id}: {e}")
                await interaction.response.send_message("❌ Impossible de mettre à jour le thème.", ephemeral=True)


    class InfoProfilView(View):
        def __init__(self, user: discord.User):
            super().__init__(timeout=120)
            self.user = user
            self.page = 0
            self.embeds = self.create_embeds()
    
            self.commandes_button = Button(label="📘 Commandes", style=ButtonStyle.primary)
            self.fonctionnalites_button = Button(label="🌟 Fonctionnalités", style=ButtonStyle.secondary)
    
            self.commandes_button.callback = self.show_commandes
            self.fonctionnalites_button.callback = self.show_fonctionnalites
    
            self.add_item(self.commandes_button)
            self.add_item(self.fonctionnalites_button)
    
        def create_embeds(self):
            commandes_embed = Embed(
                title="📘 Commandes du Système de Profil",
                description=(
                    "Voici les commandes disponibles :\n\n"
                    "• `/myprofil` : crée ou modifie ton profil\n"
                    "• `/profil` : affiche ton profil ou celui d’un autre membre\n"
                    "• `/delete_profil` : supprime une ou plusieurs infos de ton profil\n"
                    "• `/secret_profil` : masque ton profil sur certains serveurs\n"
                    "• `/unhide_profil` : rend ton profil à nouveau visible\n"
                    "• `/info_profil` : affiche ces informations\n\n"
                    "**Toutes ces commandes sont utilisables sur tous les serveurs où Etherya est présent.**"
                ),
                color=discord.Color.blurple()
            )
            commandes_embed.set_thumbnail(url=self.user.display_avatar.url)
            commandes_embed.set_footer(text="Etherya — Page 1/2")
    
            fonctionnalites_embed = Embed(
                title="🌟 Fonctionnalités du Profil Etherya",
                description=(
                    "Voici ce que propose le système de profil :\n\n"
                    "🎨 **Thème visuel** : Personnalise l'apparence de ton profil\n"
                    "🎂 **Anniversaire** : Etherya te le souhaite dans un salon dédié !\n"
                    "🏷️ **Badges dynamiques** :\n"
                    "• 👑 Staff : pour les admins/mods\n"
                    "• 📅 Ancien : membre depuis > 3 mois\n"
                    "• 🚫 Profil caché : si tu l’as masqué sur ce serveur\n"
                    "👥 **Visibilité serveur** : rends ton profil visible ou non selon les serveurs"
                ),
                color=discord.Color.green()
            )
            fonctionnalites_embed.set_thumbnail(url=self.user.display_avatar.url)
            fonctionnalites_embed.set_image(url="https://github.com/Cass64/EtheryaBot/blob/main/images_etherya/banniere_profil.png?raw=true")
            fonctionnalites_embed.set_footer(text="Etherya — Page 2/2")
    
            return [commandes_embed, fonctionnalites_embed]
    
        async def show_commandes(self, interaction: Interaction):
            self.page = 0
            self.commandes_button.style = ButtonStyle.primary
            self.fonctionnalites_button.style = ButtonStyle.secondary
            await interaction.response.edit_message(embed=self.embeds[self.page], view=self)
    
        async def show_fonctionnalites(self, interaction: Interaction):
            self.page = 1
            self.commandes_button.style = ButtonStyle.secondary
            self.fonctionnalites_button.style = ButtonStyle.primary
            await interaction.response.edit_message(embed=self.embeds[self.page], view=self)


    @app_commands.command(name="myprofil", description="Créer ou modifier ton profil personnel")
    async def myprofil(self, interaction: discord.Interaction,
                       surnom: str = None, photo: str = None, hobby: str = None, aime: str = None,
                       aime_pas: str = None, lieu: str = None, metier: str = None, sexe: str = None,
                       situation: str = None, citation: str = None, anniversaire: str = None,
                       animal_prefere: str = None):
        try:
            # Validation de l'anniversaire avant d'enregistrer
            if anniversaire:
                if not validate_birthday(anniversaire):
                    await interaction.response.send_message("❌ Le format de l'anniversaire est invalide. Utilise le format DD/MM/YYYY.", ephemeral=True)
                    return  # Arrêter ici si le format est invalide

            # Récupérer le profil existant ou créer un profil vide
            profil = await get_user_profile(interaction.user.id) or {}
            profil.update({
                "pseudo": interaction.user.name,
                "surnom": surnom or profil.get("surnom"),
                "photo": photo or profil.get("photo"),
                "hobby": hobby or profil.get("hobby"),
                "aime": aime or profil.get("aime"),
                "aime_pas": aime_pas or profil.get("aime_pas"),
                "lieu": lieu or profil.get("lieu"),
                "metier": metier or profil.get("metier"),
                "sexe": sexe or profil.get("sexe"),
                "situation": situation or profil.get("situation"),
                "citation": citation or profil.get("citation"),
                "anniversaire": anniversaire or profil.get("anniversaire"),
                "animal_prefere": animal_prefere or profil.get("animal_prefere"),
            })

            # Sauvegarder ou mettre à jour le profil
            await save_user_profile(interaction.user.id, profil)

            # Créer une vue pour permettre à l'utilisateur de choisir un thème
            view = View()
            view.add_item(self.ThemeSelect(interaction.user.id))

            await interaction.response.send_message(
                content="✅ Tes informations de profil ont été enregistrées ou mises à jour ! Choisis un thème de couleur pour ton profil.",
                view=view, ephemeral=True
            )

        except Exception as e:
            print(f"❌ Erreur /myprofil : {e}")
            await interaction.response.send_message("❌ Une erreur est survenue.", ephemeral=True)

    @app_commands.command(name="profil", description="Voir le profil d'un membre")
    async def profil(self, interaction: discord.Interaction, user: discord.User = None):
        try:
            user = user or interaction.user
            # Vérifie que l'utilisateur ciblé est bien dans le serveur
            if user.id != interaction.user.id and not interaction.guild.get_member(user.id):
                await interaction.response.send_message(
                    "❌ Tu ne peux consulter le profil d'un utilisateur qui n'est pas présent sur ce serveur.",
                    ephemeral=True
                )
                return
            profil = await get_user_profile(user.id)
    
            if not profil:
                await interaction.response.send_message("❌ Ce membre n'a pas encore créé son profil avec /myprofil.", ephemeral=True)
                return
    
            # Vérification si le profil est caché sur ce serveur
            if str(interaction.guild.id) in profil.get("hidden_on_servers", []):
                await interaction.response.send_message("❌ Ce membre a choisi de ne pas rendre son profil visible ici.", ephemeral=True)
                return
    
            couleur_debut = profil.get("couleur_debut", "#3498db")
            couleur_rgb = discord.Color.from_rgb(int(couleur_debut[1:3], 16),
                                                 int(couleur_debut[3:5], 16),
                                                 int(couleur_debut[5:7], 16))
    
            embed = discord.Embed(
                title=f"📋 Profil de {profil.get('pseudo', user.name)}",
                description="Voici les informations personnelles et celles liées à ce serveur 👇",
                color=couleur_rgb,
                timestamp=discord.utils.utcnow()
            )
    
            embed.set_thumbnail(url=profil.get("photo", user.display_avatar.url))
            embed.set_image(url="https://github.com/Cass64/EtheryaBot/blob/main/images_etherya/banniere_profil.png?raw=true")
    
            personnels = [
                ("📝 Surnom", profil.get("surnom", "Non renseigné")),
                ("🎯 Hobby", profil.get("hobby", "Non renseigné")),
                ("💖 Aime", profil.get("aime", "Non renseigné")),
                ("💔 Aime pas", profil.get("aime_pas", "Non renseigné")),
                ("📍 Lieu", profil.get("lieu", "Non renseigné")),
                ("💼 Métier", profil.get("metier", "Non renseigné")),
                ("⚧️ Sexe", profil.get("sexe", "Non renseigné")),
                ("💞 Situation", profil.get("situation", "Non renseigné")),
                ("📜 Citation", profil.get("citation", "Non renseigné")),
                ("🎂 Anniversaire", profil.get("anniversaire", "Non renseigné")),
                ("🐶 Animal préféré", profil.get("animal_prefere", "Non renseigné")),
            ]
    
            for name, value in personnels:
                if value and value != "Non renseigné":
                    embed.add_field(name=name, value=value, inline=True)
    
            member = interaction.guild.get_member(user.id)
            badges = []
    
            if member:
                if any(role.permissions.administrator for role in member.roles):
                    badges.append("👑 Staff")
                if member.joined_at and (datetime.utcnow() - member.joined_at.replace(tzinfo=None)).days >= 90:
                    badges.append("📅 Ancien membre")
    
                # Vérifier si le profil est caché sur ce serveur (par ID)
                if str(interaction.guild.id) in profil.get("hidden_on_servers", []):
                    badges.append("🚫 Profil caché sur ce serveur")
    
            badge_text = " | ".join(badges) if badges else "Aucun badge"
    
            embed.add_field(name="📌 Badges liés au serveur", value=badge_text, inline=False)
            embed.set_footer(text=f"Thème : {profil.get('theme', 'Non défini')}", icon_url=interaction.client.user.display_avatar.url)
    
            await interaction.response.send_message(embed=embed)
    
        except Exception as e:
            print(f"❌ Erreur /profil : {e}")
            await interaction.response.send_message("❌ Une erreur est survenue lors de l'affichage du profil.", ephemeral=True)

    @app_commands.command(name="info_profil", description="Affiche les infos sur le système de profil Etherya")
    async def info_profil(self, interaction: Interaction):
        view = InfoProfilView(interaction.user)
        await interaction.response.send_message(embed=view.embeds[0], view=view)

    @app_commands.command(name="delete_profil", description="Supprimer une ou plusieurs informations de ton profil")
    async def delete_profil(self, interaction: discord.Interaction):
        profil = await get_user_profile(interaction.user.id)
        if not profil:
            await interaction.response.send_message("❌ Tu n'as pas encore de profil à modifier.", ephemeral=True)
            return
    
        class DeleteSelect(discord.ui.Select):
            def __init__(self):
                options = [
                    discord.SelectOption(label="🗑️ Tout supprimer", value="__ALL__", description="Supprime tout ton profil"),
                ]
                for key in [
                    "surnom", "photo", "hobby", "aime", "aime_pas", "lieu", "metier",
                    "sexe", "situation", "citation", "anniversaire", "animal_prefere", "theme"
                ]:
                    label = key.replace("_", " ").capitalize()
                    options.append(discord.SelectOption(label=label, value=key))
    
                super().__init__(
                    placeholder="Sélectionne les informations à supprimer",
                    min_values=1,
                    max_values=len(options),
                    options=options
                )
    
            async def callback(self, interaction_select: discord.Interaction):
                try:
                    if "__ALL__" in self.values:
                        await delete_user_fields(interaction.user.id, [
                            "surnom", "photo", "hobby", "aime", "aime_pas", "lieu", "metier",
                            "sexe", "situation", "citation", "anniversaire", "animal_prefere", "theme"
                        ])
                        await interaction_select.response.edit_message(content="✅ Ton profil a été complètement supprimé.", embed=None, view=None)
                    else:
                        await delete_user_fields(interaction.user.id, self.values)
                        await interaction_select.response.edit_message(content=f"✅ Informations supprimées : {', '.join(self.values)}", embed=None, view=None)
    
                except Exception as e:
                    await interaction_select.response.send_message(f"❌ Une erreur est survenue lors de la suppression : {e}", ephemeral=True)
    
        view = discord.ui.View()
        view.add_item(DeleteSelect())
    
        await interaction.response.send_message("🗑️ Choisis les informations de ton profil que tu veux supprimer :", view=view, ephemeral=True)

    @app_commands.command(name="secret_profil", description="Cacher ton profil sur certains serveurs")
    async def secret_profil(self, interaction: discord.Interaction):
        try:
            user_id = interaction.user.id
            profil = await get_user_profile(user_id)
    
            if not profil:
                await interaction.response.send_message("❌ Tu n'as pas encore de profil. Utilise `/myprofil` pour en créer un.", ephemeral=True)
                return
    
            # Liste des serveurs où l'utilisateur est présent (en utilisant les IDs)
            server_ids = [str(guild.id) for guild in self.bot.guilds if guild.get_member(user_id)]
            server_names = [guild.name for guild in self.bot.guilds if guild.get_member(user_id)]
            if not server_ids:
                await interaction.response.send_message("❌ Tu n'es membre d'aucun serveur où le bot est présent.", ephemeral=True)
                return
    
            # Création du menu déroulant pour choisir les serveurs où cacher le profil
            class SecretSelect(discord.ui.Select):
                def __init__(self, server_ids, server_names):
                    options = [
                        discord.SelectOption(label=server, value=server_id) for server_id, server in zip(server_ids, server_names)
                    ]
                    super().__init__(placeholder="Choisis les serveurs où cacher ton profil", min_values=1, max_values=len(options), options=options)
    
                async def callback(self, interaction_select: discord.Interaction):
                    # Cacher le profil sur les serveurs sélectionnés
                    selected_servers = self.values
                    profil['hidden_on_servers'] = selected_servers  # Stocke les IDs des serveurs
                    await save_user_profile(user_id, profil)
                    await interaction_select.response.edit_message(
                        content=f"✅ Ton profil est désormais caché sur les serveurs : {', '.join(selected_servers)}",
                        view=None
                    )
    
            view = discord.ui.View()
            view.add_item(SecretSelect(server_ids, server_names))
            await interaction.response.send_message(
                "🔒 Sélectionne les serveurs où tu souhaites cacher ton profil.", view=view, ephemeral=True
            )
    
        except Exception as e:
            print(f"❌ Erreur dans la commande /secret_profil : {e}")
            await interaction.response.send_message("❌ Une erreur est survenue.", ephemeral=True)


    @app_commands.command(name="unhide_profil", description="Rendre ton profil visible à nouveau sur certains serveurs")
    async def unhide_profil(self, interaction: discord.Interaction):
        try:
            user_id = interaction.user.id
            profil = await get_user_profile(user_id)
    
            if not profil or 'hidden_on_servers' not in profil:
                await interaction.response.send_message("❌ Tu n'as pas de profil caché. Utilise `/secret_profil` pour le cacher.", ephemeral=True)
                return
    
            # Liste des serveurs où l'utilisateur peut rendre son profil visible (en utilisant les IDs)
            hidden_servers = profil['hidden_on_servers']
            if not hidden_servers:
                await interaction.response.send_message("❌ Il n'y a aucun serveur où ton profil est caché.", ephemeral=True)
                return
    
            # Création du menu déroulant pour choisir les serveurs où rendre visible le profil
            class UnhideSelect(discord.ui.Select):
                def __init__(self, hidden_servers):
                    options = [
                        discord.SelectOption(label=server_id, value=server_id) for server_id in hidden_servers
                    ]
                    super().__init__(placeholder="Choisis les serveurs où rendre ton profil visible", min_values=1, max_values=len(options), options=options)
    
                async def callback(self, interaction_select: discord.Interaction):
                    # Rendre visible le profil sur les serveurs sélectionnés
                    selected_servers = self.values
                    profil['hidden_on_servers'] = [server for server in profil['hidden_on_servers'] if server not in selected_servers]
                    await save_user_profile(user_id, profil)
                    await interaction_select.response.edit_message(
                        content=f"✅ Ton profil est maintenant visible sur les serveurs : {', '.join(selected_servers)}",
                        view=None
                    )
    
            view = discord.ui.View()
            view.add_item(UnhideSelect(hidden_servers))
            await interaction.response.send_message(
                "👀 Sélectionne les serveurs où tu souhaites rendre ton profil visible.", view=view, ephemeral=True
            )
    
        except Exception as e:
            print(f"❌ Erreur dans la commande /unhide_profil : {e}")
            await interaction.response.send_message("❌ Une erreur est survenue.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Profil(bot))
