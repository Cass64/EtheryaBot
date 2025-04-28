import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Select, View
from utils.database import get_user_profile, save_user_profile

COULEURS = {
    "Bleu Ciel": ("#3498db", "#1abc9c"),
    "Rouge Passion": ("#e74c3c", "#c0392b"),
    "Violet Mystère": ("#9b59b6", "#8e44ad"),
    "Noir Élégant": ("#2c3e50", "#34495e"),
}

class Profil(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def ask_for_field(self, interaction, field_name, description, placeholder):
        """Fonction pour demander un champ et afficher une description claire"""
        await interaction.response.send_message(f"🔄 {description} (ex: {placeholder})", ephemeral=True)
        msg = await self.bot.wait_for('message', check=lambda m: m.author == interaction.user, timeout=60.0)
        return msg.content if msg else None

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
        """Commande principale pour la création ou la modification du profil avec prompts pour chaque champ"""

        try:
            # Demande des informations avec des prompts
            surnom = await self.ask_for_field(interaction, "Surnom", "Ton surnom ou un autre nom que tes amis utilisent pour t'appeler", "ex: John")
            photo = await self.ask_for_field(interaction, "Photo", "Lien vers une photo de toi (facultatif)", "ex: https://imageurl.com/photo.jpg")
            hobby = await self.ask_for_field(interaction, "Hobby", "Ton hobby ou activité préférée", "ex: Jouer au football")
            aime = await self.ask_for_field(interaction, "Aime", "Les choses que tu aimes", "ex: Les chats, le chocolat")
            aime_pas = await self.ask_for_field(interaction, "Aime Pas", "Les choses que tu n'aimes pas", "ex: Les brocolis")
            lieu = await self.ask_for_field(interaction, "Lieu", "Où tu habites", "ex: Paris")
            metier = await self.ask_for_field(interaction, "Métier", "Ton métier ou domaine d'activité", "ex: Développeur web")
            sexe = await self.ask_for_field(interaction, "Sexe", "Ton sexe (Homme, Femme, Autre)", "ex: Homme")
            situation = await self.ask_for_field(interaction, "Situation Amoureuse", "Ton état civil actuel", "ex: En couple")
            citation = await self.ask_for_field(interaction, "Citation Favorite", "Ta citation préférée qui t'inspire", "ex: 'Carpe Diem'")
            anniversaire = await self.ask_for_field(interaction, "Anniversaire", "Ta date d'anniversaire (format: jj/mm)", "ex: 25/12")
            animal_prefere = await self.ask_for_field(interaction, "Animal Préféré", "Ton animal préféré", "ex: Chat")

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

            await interaction.response.send_message("✅ Tes informations de profil ont été enregistrées !", ephemeral=True)

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
                color=discord.Color.from_rgb(52, 152, 219),
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
