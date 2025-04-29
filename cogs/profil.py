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
        self.tree = bot.tree

    async def cog_load(self):
        self.bot.tree.add_command(self.myprofil)
        self.bot.tree.add_command(self.profil)
        self.bot.tree.add_command(self.info_profil)
        self.bot.tree.add_command(self.delete_profil)
        self.bot.tree.add_command(self.secret_profil)
        self.bot.tree.add_command(self.unhide_profil)

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

            if "hidden_on_servers" in profil and str(interaction.guild.id) in profil["hidden_on_servers"] and user.id != interaction.user.id:
                await interaction.response.send_message("🔒 Ce membre a choisi de cacher son profil sur ce serveur.", ephemeral=True)
                return

            couleur_hex = profil.get("couleur_debut", "#3498db")
            try:
                couleur_rgb = discord.Color.from_rgb(
                    int(couleur_hex[1:3], 16),
                    int(couleur_hex[3:5], 16),
                    int(couleur_hex[5:7], 16)
                )
            except:
                couleur_rgb = discord.Color.blue()

            embed = discord.Embed(
                title=f"📋 Profil de {profil.get('pseudo') or user.name}",
                description="Voici les informations personnelles et celles liées à ce serveur 👇",
                color=couleur_rgb,
                timestamp=datetime.utcnow()
            )

            embed.set_thumbnail(url=profil.get("photo") or user.display_avatar.url)
            embed.set_image(url="https://github.com/Cass64/EtheryaBot/blob/main/images_etherya/banniere_profil.png?raw=true")

            personnels = {
                "📝 Surnom": "surnom",
                "🎯 Hobby": "hobby",
                "💖 Aime": "aime",
                "💔 Aime pas": "aime_pas",
                "📍 Lieu": "lieu",
                "💼 Métier": "metier",
                "⚧️ Sexe": "sexe",
                "💞 Situation": "situation",
                "📜 Citation": "citation",
                "🎂 Anniversaire": "anniversaire",
                "🐶 Animal préféré": "animal_prefere",
            }

            for name, key in personnels.items():
                value = profil.get(key)
                if value and value.strip().lower() != "non renseigné":
                    embed.add_field(name=name, value=value, inline=True)

            member = interaction.guild.get_member(user.id)
            badges = []

            if member:
                if any(role.permissions.administrator for role in member.roles if role.name != "@everyone"):
                    badges.append("👑 Staff")
                if member.joined_at and (datetime.utcnow() - member.joined_at.replace(tzinfo=None)).days >= 90:
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
                description=(...),
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
                    discord.SelectOption(label="🗑️ Tout supprimer", value="__ALL__"),
                ] + [
                    discord.SelectOption(label=key.replace("_", " ").capitalize(), value=key)
                    for key in [
                        "surnom", "photo", "hobby", "aime", "aime_pas", "lieu", "metier",
                        "sexe", "situation", "citation", "anniversaire", "animal_prefere", "theme"
                    ]
                ]
                super().__init__(placeholder="Sélectionne les infos à supprimer", min_values=1, max_values=len(options), options=options)

            async def callback(self, interaction_select: discord.Interaction):
                profil = await get_user_profile(interaction.user.id)
                if "__ALL__" in self.values:
                    await save_user_profile(interaction.user.id, {})
                    await interaction_select.response.edit_message(content="✅ Ton profil a été complètement supprimé.", view=None)
                else:
                    for key in self.values:
                        profil.pop(key, None)
                    await save_user_profile(interaction.user.id, profil)
                    await interaction_select.response.edit_message(
                        content=f"✅ Infos supprimées : {', '.join(self.values)}", view=None
                    )

        view = discord.ui.View()
        view.add_item(DeleteSelect())
        await interaction.response.send_message("🗑️ Choisis les infos de ton profil à supprimer :", view=view, ephemeral=True)

    @app_commands.command(name="secret_profil", description="Cacher ton profil sur certains serveurs")
    async def secret_profil(self, interaction: discord.Interaction):
        try:
            user_id = interaction.user.id
            profil = await get_user_profile(user_id)
            if not profil:
                await interaction.response.send_message("❌ Tu n'as pas encore de profil.", ephemeral=True)
                return

            server_ids = [str(guild.id) for guild in self.bot.guilds if guild.get_member(user_id)]
            if not server_ids:
                await interaction.response.send_message("❌ Aucun serveur détecté.", ephemeral=True)
                return

            class SecretSelect(discord.ui.Select):
                def __init__(self):
                    options = [
                        discord.SelectOption(label=self.bot.get_guild(int(sid)).name, value=sid)
                        for sid in server_ids
                    ]
                    super().__init__(placeholder="Choisis les serveurs à cacher", min_values=1, max_values=len(options), options=options)

                async def callback(self, interaction_select: discord.Interaction):
                    profil["hidden_on_servers"] = self.values
                    await save_user_profile(user_id, profil)
                    noms = [self.bot.get_guild(int(i)).name for i in self.values]
                    await interaction_select.response.edit_message(
                        content=f"✅ Ton profil est caché sur : {', '.join(noms)}", view=None
                    )

            view = discord.ui.View()
            view.add_item(SecretSelect())
            await interaction.response.send_message("🔒 Sélectionne les serveurs :", view=view, ephemeral=True)

        except Exception as e:
            print(f"❌ Erreur /secret_profil : {e}")
            await interaction.response.send_message("❌ Une erreur est survenue.", ephemeral=True)

    @app_commands.command(name="unhide_profil", description="Rendre ton profil visible à nouveau sur certains serveurs")
    async def unhide_profil(self, interaction: discord.Interaction):
        try:
            user_id = interaction.user.id
            profil = await get_user_profile(user_id)
            hidden = profil.get("hidden_on_servers", [])

            if not hidden:
                await interaction.response.send_message("❌ Aucun serveur caché détecté.", ephemeral=True)
                return

            class UnhideSelect(discord.ui.Select):
                def __init__(self):
                    options = [
                        discord.SelectOption(label=self.bot.get_guild(int(sid)).name, value=sid)
                        for sid in hidden
                    ]
                    super().__init__(placeholder="Choisis les serveurs à afficher", min_values=1, max_values=len(options), options=options)

                async def callback(self, interaction_select: discord.Interaction):
                    profil["hidden_on_servers"] = [sid for sid in hidden if sid not in self.values]
                    await save_user_profile(user_id, profil)
                    noms = [self.bot.get_guild(int(i)).name for i in self.values]
                    await interaction_select.response.edit_message(
                        content=f"✅ Ton profil est visible sur : {', '.join(noms)}", view=None
                    )

            view = discord.ui.View()
            view.add_item(UnhideSelect())
            await interaction.response.send_message("👀 Choisis les serveurs :", view=view, ephemeral=True)

        except Exception as e:
            print(f"❌ Erreur /unhide_profil : {e}")
            await interaction.response.send_message("❌ Une erreur est survenue.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Profil(bot))
