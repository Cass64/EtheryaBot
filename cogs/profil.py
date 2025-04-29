import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Select, View, Button
from utils.database import get_user_profile, save_user_profile
from datetime import datetime

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

    @app_commands.command(name="myprofil", description="Créer ou modifier ton profil personnel")
    async def myprofil(self, interaction: discord.Interaction,
                       surnom: str = None, photo: str = None, hobby: str = None, aime: str = None,
                       aime_pas: str = None, lieu: str = None, metier: str = None, sexe: str = None,
                       situation: str = None, citation: str = None, anniversaire: str = None,
                       animal_prefere: str = None):
        try:
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

            await save_user_profile(interaction.user.id, profil)

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
            profil = await get_user_profile(user.id)
            if not profil:
                await interaction.response.send_message("❌ Ce membre n'a pas encore créé son profil avec /myprofil.", ephemeral=True)
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
                if (datetime.utcnow() - member.joined_at.replace(tzinfo=None)).days >= 90:
                    badges.append("📅 Ancien membre")

            badge_text = " | ".join(badges) if badges else "Aucun badge"

            embed.add_field(name="📌 Badges liés au serveur", value=badge_text, inline=False)
            embed.set_footer(text=f"Thème : {profil.get('theme', 'Non défini')}", icon_url=interaction.client.user.display_avatar.url)

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            print(f"❌ Erreur /profil : {e}")
            await interaction.response.send_message("❌ Une erreur est survenue lors de l'affichage du profil.", ephemeral=True)

    @app_commands.command(name="info_profil", description="Informations sur le système de profil")
    async def info_profil(self, interaction: discord.Interaction):
        try:
            embed = discord.Embed(
                title="📘 Informations sur le Profil Utilisateur",
                description=(
                    "Bienvenue dans le système de **profil utilisateur** d’Etherya Bot !\n\n"
                    "🔹 Chaque membre peut créer un **profil personnalisé**, visible **publiquement** "
                    "sur **tous les serveurs** où le bot est présent.\n\n"
                    "🎨 Tu peux configurer ton thème de profil, ta photo, ton surnom, ton hobby, ce que tu aimes, "
                    "et plein d'autres détails pour te représenter au mieux.\n\n"
                    "🏷️ Des **badges dynamiques** sont ajoutés automatiquement selon ta présence ou ton rôle sur chaque serveur "
                    "(comme `Staff`, `Ancien`, etc.).\n\n"
                    "📌 Utilise la commande `/myprofil` pour personnaliser ton profil à tout moment.\n\n"
                    "📂 Ensuite, consulte ton profil (ou celui d'un autre membre) avec `/profil`.\n\n"
                    "**Ton profil te suit partout, sois fier de qui tu es ! ✨**"
                ),
                color=discord.Color.blurple(),
                timestamp=discord.utils.utcnow()
            )

            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            embed.set_image(url="https://github.com/Cass64/EtheryaBot/blob/main/images_etherya/banniere_profil.png?raw=true")
            embed.set_footer(text="Système de Profil Etherya", icon_url=interaction.client.user.display_avatar.url)
            embed.set_author(name="🧾 Système de Profil Global")

            bouton = Button(label="✏️ Modifier mon profil", style=discord.ButtonStyle.primary)

            async def bouton_callback(bouton_interaction: discord.Interaction):
                if bouton_interaction.user.id != interaction.user.id:
                    await bouton_interaction.response.send_message("❌ Ce bouton ne t'est pas destiné.", ephemeral=True)
                    return
                await bouton_interaction.response.send_message(
                    "🛠️ Utilise simplement la commande `/myprofil` pour personnaliser ton profil !",
                    ephemeral=True
                )

            bouton.callback = bouton_callback
            view = View()
            view.add_item(bouton)

            await interaction.response.send_message(embed=embed, view=view)

        except Exception as e:
            print(f"❌ Erreur dans la commande /info_profil : {e}")
            await interaction.response.send_message("❌ Une erreur est survenue lors de l'envoi des informations.", ephemeral=True)

    @app_commands.command(name="delete_profil", description="Supprimer une ou plusieurs informations de ton profil")
    async def delete_profil(self, interaction: discord.Interaction):
        profil = await get_user_profile(interaction.user.id)
        if not profil:
            await interaction.response.send_message("❌ Tu n'as pas encore de profil à modifier.", ephemeral=True)
            return

        class DeleteSelect(discord.ui.Select):
            def __init__(self):
                options = [
                    discord.SelectOption(label="🗑️ Tout supprimer", value="__ALL__", description="Supprimer toutes les informations"),
                    discord.SelectOption(label="📝 Surnom", value="surnom"),
                    discord.SelectOption(label="📷 Photo", value="photo"),
                    discord.SelectOption(label="🎯 Hobby", value="hobby"),
                    discord.SelectOption(label="💖 Aime", value="aime"),
                    discord.SelectOption(label="💔 Aime pas", value="aime_pas"),
                    discord.SelectOption(label="📍 Lieu", value="lieu"),
                    discord.SelectOption(label="💼 Métier", value="metier"),
                    discord.SelectOption(label="⚧️ Sexe", value="sexe"),
                    discord.SelectOption(label="💞 Situation", value="situation"),
                    discord.SelectOption(label="📜 Citation", value="citation"),
                    discord.SelectOption(label="🎂 Anniversaire", value="anniversaire"),
                    discord.SelectOption(label="🐶 Animal préféré", value="animal_prefere")
                ]
                super().__init__(placeholder="Sélectionne ce que tu veux supprimer", min_values=1, max_values=len(options), options=options)

            async def callback(self, interaction: discord.Interaction):
                if str(interaction.user.id) != str(self.user_id):
                    await interaction.response.send_message("❌ Tu ne peux pas supprimer les informations d'un autre utilisateur.", ephemeral=True)
                    return

                selection = self.values
                if "ALL" in selection:
                    await save_user_profile(interaction.user.id, {})
                    await interaction.response.send_message("❌ Toutes les informations de ton profil ont été supprimées.", ephemeral=True)
                    return

                for key in selection:
                    if key in profil:
                        del profil[key]

                await save_user_profile(interaction.user.id, profil)
                await interaction.response.send_message("✅ Les informations sélectionnées ont été supprimées.", ephemeral=True)

        select = DeleteSelect()
        view = View()
        view.add_item(select)
        await interaction.response.send_message("Sélectionne les informations que tu souhaites supprimer de ton profil :", view=view)

 # Commande pour cacher le profil sur certains serveurs
    @app_commands.command(name="secret_profil", description="Cacher ton profil sur certains serveurs")
    async def secret_profil(self, interaction: discord.Interaction):
        try:
            profil = await get_user_profile(interaction.user.id)
            if not profil:
                await interaction.response.send_message("❌ Tu n'as pas encore de profil. Crée-le avec `/myprofil`.", ephemeral=True)
                return

            hidden_servers = profil.get("hidden_servers", [])
            servers = [guild.name for guild in self.bot.guilds if guild.id not in hidden_servers]

            if not servers:
                await interaction.response.send_message("❌ Tu n'es pas dans d'autres serveurs où tu peux cacher ton profil.", ephemeral=True)
                return

            options = [discord.SelectOption(label=server, value=str(guild.id)) for guild in self.bot.guilds if guild.id not in hidden_servers]

            if not options:
                await interaction.response.send_message("❌ Aucun serveur disponible où cacher ton profil.", ephemeral=True)
                return

            select = Select(placeholder="Choisis un serveur où cacher ton profil", min_values=1, max_values=len(options), options=options)

            async def select_callback(select_interaction: discord.Interaction):
                selected_servers = select_interaction.data["values"]
                profil["hidden_servers"].extend([int(server_id) for server_id in selected_servers])
                await save_user_profile(interaction.user.id, profil)

                await select_interaction.response.send_message("✅ Ton profil a été caché sur les serveurs sélectionnés.", ephemeral=True)

            select.callback = select_callback
            view = View()
            view.add_item(select)

            await interaction.response.send_message("Sélectionne les serveurs où tu souhaites cacher ton profil :", view=view)

        except Exception as e:
            print(f"❌ Erreur dans la commande /secret_profil : {e}")
            await interaction.response.send_message("❌ Une erreur est survenue.", ephemeral=True)

    # Commande pour révéler le profil caché sur certains serveurs
    @app_commands.command(name="unhide_profil", description="Révéler ton profil sur certains serveurs")
    async def unhide_profil(self, interaction: discord.Interaction):
        try:
            profil = await get_user_profile(interaction.user.id)
            if not profil:
                await interaction.response.send_message("❌ Tu n'as pas encore de profil. Crée-le avec `/myprofil`.", ephemeral=True)
                return

            hidden_servers = profil.get("hidden_servers", [])
            if not hidden_servers:
                await interaction.response.send_message("❌ Ton profil n'est caché sur aucun serveur.", ephemeral=True)
                return

            servers = [guild.name for guild in self.bot.guilds if guild.id in hidden_servers]

            if not servers:
                await interaction.response.send_message("❌ Aucun serveur trouvé où ton profil est caché.", ephemeral=True)
                return

            options = [discord.SelectOption(label=server, value=str(guild.id)) for guild in self.bot.guilds if guild.id in hidden_servers]

            select = Select(placeholder="Choisis un serveur où révéler ton profil", min_values=1, max_values=len(options), options=options)

            async def select_callback(select_interaction: discord.Interaction):
                selected_servers = select_interaction.data["values"]
                profil["hidden_servers"] = [guild_id for guild_id in hidden_servers if str(guild_id) not in selected_servers]
                await save_user_profile(interaction.user.id, profil)

                await select_interaction.response.send_message("✅ Ton profil a été révélé sur les serveurs sélectionnés.", ephemeral=True)

            select.callback = select_callback
            view = View()
            view.add_item(select)

            await interaction.response.send_message("Sélectionne les serveurs où tu souhaites révéler ton profil :", view=view)

        except Exception as e:
            print(f"❌ Erreur dans la commande /unhide_profil : {e}")
            await interaction.response.send_message("❌ Une erreur est survenue.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Profil(bot))
