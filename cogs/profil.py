import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Select, View
from utils.database import get_user_profile, save_user_profile, delete_user_fields
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


    @app_commands.command(name="myprofil_jeux", description="Définis ou modifie ton top 3 jeux vidéo")
    async def myprofil_jeux(self, interaction: discord.Interaction,
        jeu1: str = None, pseudo1: str = None, heures1: int = None, rank1: str = None, mate1: str = None,
        jeu2: str = None, pseudo2: str = None, heures2: int = None, rank2: str = None, mate2: str = None,
        jeu3: str = None, pseudo3: str = None, heures3: int = None, rank3: str = None, mate3: str = None):
    
        profil = await get_user_profile(interaction.user.id) or {}
        anciens_jeux = profil.get("jeux_video", [{}, {}, {}])
    
        nouveaux_jeux = []
        for i, infos in enumerate([
            (jeu1, pseudo1, heures1, rank1, mate1),
            (jeu2, pseudo2, heures2, rank2, mate2),
            (jeu3, pseudo3, heures3, rank3, mate3),
        ]):
            jeu_data = anciens_jeux[i] if i < len(anciens_jeux) else {}
    
            keys = ["jeu", "pseudo", "heures", "rank", "mate"]
            for k, v in zip(keys, infos):
                if v is not None:
                    jeu_data[k] = v  # Met à jour uniquement les valeurs fournies
    
            if any(jeu_data.values()):  # On garde uniquement s'il y a au moins une info
                nouveaux_jeux.append(jeu_data)
    
        profil["jeux_video"] = nouveaux_jeux
        await save_user_profile(interaction.user.id, profil)
    
        await interaction.response.send_message("✅ Ton profil jeux vidéo a bien été mis à jour !", ephemeral=True)



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
        user = user or interaction.user
        profil = await get_user_profile(user.id)

        if not profil:
            await interaction.response.send_message("❌ Ce membre n'a pas encore créé son profil.", ephemeral=True)
            return

        class SectionSelect(discord.ui.Select):
            def __init__(self):
                options = [
                    discord.SelectOption(label="🎭 Profil personnel", value="personnel"),
                    discord.SelectOption(label="🎮 Profil jeux vidéo", value="jeux"),
                ]
                super().__init__(placeholder="🔽 Choisis une section du profil", options=options)

            async def callback(self, interaction_select: discord.Interaction):
                await interaction_select.response.edit_message(embed=create_embed(self.values[0]), view=self.view)

        def create_embed(section):
            couleur = profil.get("couleur_debut", "#7289DA")
            rgb = discord.Color.from_rgb(int(couleur[1:3], 16), int(couleur[3:5], 16), int(couleur[5:7], 16))

            if section == "personnel":
                embed = discord.Embed(
                    title=f"📋 Profil de {profil.get('pseudo', user.name)}",
                    description="Voici les informations personnelles et celles liées au serveur 👇",
                    color=rgb,
                    timestamp=discord.utils.utcnow()
                )
                embed.set_thumbnail(url=profil.get("photo", user.display_avatar.url))
                embed.set_image(url="https://github.com/Cass64/EtheryaBot/blob/main/images_etherya/banniere_profil.png?raw=true")

                infos = [
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
                    ("🐶 Animal préféré", profil.get("animal_prefere")),
                ]
                for name, value in infos:
                    if value:
                        embed.add_field(name=name, value=value, inline=True)

                badges = []
                member = interaction.guild.get_member(user.id)
                if member:
                    if any(r.permissions.administrator for r in member.roles):
                        badges.append("👑 Staff")
                    if member.joined_at and (datetime.utcnow() - member.joined_at.replace(tzinfo=None)).days >= 90:
                        badges.append("📅 Ancien membre")

                embed.add_field(name="📌 Badges liés au serveur", value=" | ".join(badges) if badges else "Aucun badge", inline=False)
                embed.set_footer(text=f"Thème : {profil.get('theme', 'Non défini')}", icon_url=interaction.client.user.display_avatar.url)
                return embed

            elif section == "jeux":
                embed = discord.Embed(
                    title=f"🎮 Profil Gaming de {profil.get('pseudo', user.name)}",
                    description="Voici ses 3 jeux favoris, avec stats & infos 👇",
                    color=rgb
                )
                jeux = profil.get("jeux_video", [])
                for i, jeu in enumerate(jeux, start=1):
                    nom = jeu.get("jeu", "Jeu inconnu")
                    pseudo = jeu.get("pseudo", "N/A")
                    heures = jeu.get("heures", 0)
                    rank = jeu.get("rank", "Non classé")
                    mate = jeu.get("mate", "Non précisé")

                    embed.add_field(
                        name=f"🎮 Top {i} - {nom}",
                        value=f"**🎮 Pseudo** : `{pseudo}`\n"
                              f"🕒 **Heures jouées** : `{heures}h`\n"
                              f"🏆 **Rank** : `{rank}`\n"
                              f"🔍 **Cherche mate** : `{mate}`",
                        inline=False
                    )
                embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/6460/6460951.png")
                return embed

        view = View()
        select = SectionSelect()
        view.add_item(select)

        await interaction.response.send_message(embed=create_embed("personnel"), view=view)


    @app_commands.command(name="info_profil", description="Informations détaillées sur le système de profil")
    async def info_profil(self, interaction: discord.Interaction):
        try:
            embed = discord.Embed(
                title="ℹ️ Système de Profil",
                description="Voici une vue d'ensemble complète du système de profil, de ses fonctionnalités et des commandes disponibles.",
                color=discord.Color.blue(),
                timestamp=discord.utils.utcnow()
            )
    
            # Introduction générale
            embed.add_field(
                name="Qu'est-ce que le système de profil ?",
                value=( 
                    "Le système de profil permet à chaque utilisateur de personnaliser son profil avec "
                    "des informations personnelles et des éléments visuels comme un thème de couleur. "
                    "Cela crée une expérience plus personnelle et visuellement attrayante sur le serveur."
                    "\n\n"
                    "De base, ton profil sera visible sur tous les serveurs où le bot est présent, "
                    "à moins que tu choisisses de le cacher spécifiquement sur certains serveurs."
                ),
                inline=False
            )
    
            # Description des commandes
            embed.add_field(
                name="📜 Commandes disponibles",
                value=(
                    "`/myprofil` : Crée ou modifie ton profil personnel. Tu peux y ajouter des informations comme ton surnom, "
                    "tes hobbies, ton métier, etc. Lors de la création, tu peux également choisir un thème de couleur pour ton profil.\n\n"
                    "`/profil` : Permet de consulter le profil d'un autre utilisateur (ou le sien si aucune personne n'est spécifiée). "
                    "Il affiche des informations sur l'utilisateur, y compris des badges comme 'Staff' ou 'Ancien membre' selon leur statut.\n\n"
                    "`/delete_profil` : Supprime une ou plusieurs informations de ton profil. Tu peux choisir de tout supprimer ou bien de supprimer certaines informations spécifiques.\n\n"
                    "`/secret_profil` : Cacher ton profil sur certains serveurs où tu es présent. Cela empêche ton profil d'être visible sur ces serveurs.\n\n"
                    "`/unhide_profil` : Rendre ton profil visible à nouveau sur les serveurs où il est actuellement caché.\n\n"
                    "`/info_profil` : Cette commande ! Elle permet de voir un résumé complet du système de profil et de ses fonctionnalités.\n"
                ),
                inline=False
            )
    
            # Fonctionnalités spéciales
            embed.add_field(
                name="✨ Fonctionnalités spéciales",
                value=(
                    "1. **Anniversaires** 🎉 : Lorsque ton anniversaire est enregistré et qu'il arrive, le bot enverra automatiquement "
                    "un message de souhaits dans le salon prévu à cet effet.\n\n"
                    "2. **Badges** 🏅 : Le profil peut inclure des badges comme 'Staff' pour les administrateurs ou 'Ancien membre' "
                    "pour les utilisateurs présents depuis plus de 3 mois. Ces badges sont affichés dans le profil et sont dynamiques en fonction de l'utilisateur.\n\n"
                    "3. **Visibilité** 👁️ : Par défaut, ton profil est visible sur tous les serveurs où le bot est présent, "
                    "mais tu peux utiliser la commande `/secret_profil` pour le cacher sur des serveurs spécifiques et la commande `/unhide_profil` "
                    "pour le rendre à nouveau visible."
                ),
                inline=False
            )
    
            # Bannière de fin
            embed.set_footer(text="🎉 Profite de ton expérience avec le bot ! 🎉")
            embed.set_image(url="https://github.com/Cass64/EtheryaBot/blob/main/images_etherya/banniere_profil.png?raw=true")  # Remplace par l'URL de ta bannière de fin
    
            # Envoi de l'embed visible pour tout le monde
            await interaction.response.send_message(embed=embed)
    
        except Exception as e:
            print(f"❌ Erreur dans la commande /info_profil : {e}")
            await interaction.response.send_message("❌ Une erreur est survenue lors de l'affichage des informations.", ephemeral=True)


    @app_commands.command(name="delete_profil", description="Supprime des parties de ton profil")
    async def delete_profil(self, interaction: Interaction):
        profil = await get_user_profile(interaction.user.id)
        if not profil:
            await interaction.response.send_message("❌ Tu n'as pas encore de profil à supprimer.", ephemeral=True)
            return

        # Construction dynamique des options
        options = [
            SelectOption(label="🧹 Tout supprimer", value="ALL", description="Supprimer l'intégralité du profil"),
            SelectOption(label="👤 Supprimer tout le profil personnel", value="PERSONAL", description="Tous les champs personnels"),
            SelectOption(label="🎮 Supprimer tout le profil gaming", value="GAMING", description="Jeux, heures, rank, etc."),
        ]

        # Champs personnels
        personnal_fields = {
            "surnom": "📝 Surnom",
            "photo": "🖼️ Photo",
            "hobby": "🎯 Hobby",
            "aime": "💖 Aime",
            "aime_pas": "💔 Aime pas",
            "lieu": "📍 Lieu",
            "metier": "💼 Métier",
            "sexe": "⚧️ Sexe",
            "situation": "💞 Situation",
            "citation": "📜 Citation",
            "anniversaire": "🎂 Anniversaire",
            "animal_prefere": "🐶 Animal préféré",
        }
        for key, label in personnal_fields.items():
            if key in profil:
                options.append(SelectOption(label=f"🔹 {label}", value=f"FIELD:{key}"))

        # Champs jeux vidéo
        jeux = profil.get("jeux_video", [])
        for i in range(len(jeux)):
            for champ in ["jeu", "pseudo", "heures", "rank", "mate"]:
                if champ in jeux[i]:
                    champ_name = champ.capitalize() if champ != "jeu" else "Nom du jeu"
                    options.append(SelectOption(label=f"🎮 {champ_name} du jeu {i+1}", value=f"GAME:{i}:{champ}"))

        class DeleteSelect(Select):
            def __init__(self):
                super().__init__(
                    placeholder="🔽 Sélectionne ce que tu veux supprimer",
                    min_values=1,
                    max_values=len(options),
                    options=options
                )

            async def callback(self, interaction_select: Interaction):
                to_delete = {
                    "fields": [],
                    "gaming": [],
                    "all": False,
                    "personal": False
                }

                for v in self.values:
                    if v == "ALL":
                        to_delete["all"] = True
                        break
                    elif v == "PERSONAL":
                        to_delete["personal"] = True
                    elif v == "GAMING":
                        to_delete["gaming"] = ["ALL"]
                    elif v.startswith("FIELD:"):
                        to_delete["fields"].append(v.split("FIELD:")[1])
                    elif v.startswith("GAME:"):
                        _, idx, champ = v.split(":")
                        to_delete["gaming"].append((int(idx), champ))

                profil = await get_user_profile(interaction.user.id)
                if to_delete["all"]:
                    await delete_user_fields(interaction.user.id, profil.keys())
                    await interaction_select.response.edit_message(content="✅ Ton profil complet a été supprimé.", view=None)
                    return

                if to_delete["personal"]:
                    for key in list(personnal_fields.keys()):
                        profil.pop(key, None)

                for field in to_delete["fields"]:
                    profil.pop(field, None)

                if "jeux_video" in profil:
                    if to_delete["gaming"] == ["ALL"]:
                        profil.pop("jeux_video", None)
                    else:
                        for idx, champ in to_delete["gaming"]:
                            if idx < len(profil["jeux_video"]):
                                profil["jeux_video"][idx].pop(champ, None)

                await save_user_profile(interaction.user.id, profil)
                await interaction_select.response.edit_message(content="✅ Les éléments sélectionnés ont été supprimés !", view=None)

        view = View()
        view.add_item(DeleteSelect())
        await interaction.response.send_message("🗑️ Que veux-tu supprimer de ton profil ?", view=view, ephemeral=True)
        
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
