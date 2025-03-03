import os  
from dotenv import load_dotenv
from discord import app_commands
import discord
from discord.ext import commands
from keep_alive import keep_alive
import random
import json
import asyncio
import pymongo
from pymongo import MongoClient
from datetime import datetime, timedelta
import math
import aiocron

load_dotenv()

# Connexion MongoDB
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client['Cass-Eco2']
collection = db['commandes']
collection2 = db['etherya-eco']

# Vérification MongoDB
try:
    client.admin.command('ping')
    print("✅ Connexion à MongoDB réussie !")
except Exception as e:
    print(f"❌ Échec de connexion à MongoDB : {e}")
    exit()

cooldowns = {}

token = os.getenv('TOKEN_BOT_DISCORD')

# Intents et configuration du bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=".", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Le bot est connecté en tant que {bot.user} (ID: {bot.user.id})")

    # Afficher les commandes chargées
    print("📌 Commandes disponibles :")
    for command in bot.commands:
        print(f"- {command.name}")

    try:
        # Synchroniser les commandes avec Discord
        synced = await bot.tree.sync()  # Synchronisation des commandes slash
        print(f"✅ Commandes slash synchronisées : {[cmd.name for cmd in synced]}")
    except Exception as e:
        print(f"❌ Erreur de synchronisation des commandes slash : {e}")


#------------------------------------------------------------------------- Commandes d'économie : !!break

# Liste des rôles autorisés pour exécuter les commandes de modération
AUTHORIZED_ROLES = ["″ [𝑺ץ] Perm Protect !!rob"]

@bot.command(name="break")
async def breakk(ctx, membre: discord.Member):
    """Ajoute un rôle fixe à un utilisateur et retire un autre rôle fixe à l'exécutant.
       Seuls ceux ayant '[𝑺ץ] Perm Anti Protect' peuvent utiliser cette commande.
    """
    ROLE_REQUIRED = "″ [𝑺ץ] Perm Protect !!rob"  # Rôle requis pour exécuter la commande
    ROLE_TO_REMOVE_BREAK = "″ [𝑺ץ] Protect !!rob"       # Rôle à ajouter au membre ciblé
    ROLE_TO_REMOVE = "″ [𝑺ץ] Perm Protect !!rob"     # Rôle à retirer à l'exécutant

    role_required = discord.utils.get(ctx.guild.roles, name=ROLE_REQUIRED)
    role_to_remove_break = discord.utils.get(ctx.guild.roles, name=ROLE_TO_REMOVE_BREAK)
    role_to_remove = discord.utils.get(ctx.guild.roles, name=ROLE_TO_REMOVE)

    if not role_required or not role_to_remove_break or not role_to_remove:
        return await ctx.send("❌ L'un des rôles spécifiés n'existe pas.")

    if role_required not in ctx.author.roles:
        return await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")

    # Vérifie si le membre a le rôle avant de le retirer
    if role_to_remove_break not in membre.roles:
        await ctx.send(f"{membre.mention} n'a pas le rôle {role_to_remove_break.mention}. <:haram:1176229029796380702>")
    else:
        await membre.remove_roles(role_to_remove_break)
        await ctx.send(f"Le rôle {role_to_remove_break.mention} a été enlevé. <a:fete:1172810362261880873>")

    # Retirer le rôle à l'exécutant
    if role_to_remove in ctx.author.roles:
        await ctx.author.remove_roles(role_to_remove)
        await ctx.send(f"Le rôle {role_to_remove.mention} vous a été retiré. <a:emoji:1341500461475168369>")
    else:
        await ctx.send(f"{ctx.author.mention}, vous n'aviez pas le rôle {role_to_remove.mention}. ❌")

#------------------------------------------------------------------------- Commandes d'économie : !!malus

# Commande classique pour "malus"
@bot.command(name="malus")
async def malus(ctx, membre: discord.Member):
    ROLE_REQUIRED = "″ [𝑺ץ] Perm Ajout Malus"
    ROLE_TO_ADD_MALUS = "″ [𝑺ץ] Malus Temporelle"
    ROLE_TO_REMOVE_MALUS = "″ [𝑺ץ] Perm Ajout Malus"

    role_required = discord.utils.get(ctx.guild.roles, name=ROLE_REQUIRED)
    role_to_add_malus = discord.utils.get(ctx.guild.roles, name=ROLE_TO_ADD_MALUS)
    role_to_remove_malus = discord.utils.get(ctx.guild.roles, name=ROLE_TO_REMOVE_MALUS)

    if not role_required or not role_to_add_malus or not role_to_remove_malus:
        return await ctx.send("❌ L'un des rôles spécifiés n'existe pas.")

    if role_required not in ctx.author.roles:
        return await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")

    # Ajouter le rôle temporaire à l'utilisateur
    await membre.add_roles(role_to_add_malus)
    await ctx.send(f"Le rôle {role_to_add_malus.mention} a été ajouté. 🎉") 

    # Retirer le rôle à l'exécutant
    if role_to_remove_malus in ctx.author.roles:
        await ctx.author.remove_roles(role_to_remove_malus)
        await ctx.send(f"Le rôle {role_to_remove_malus.mention} a été retiré. 🎭")
    else:
        await ctx.send(f"{ctx.author.mention}, vous n'aviez pas le rôle {role_to_remove_malus.mention}. ❌")

    # Attendre 24 heures avant de retirer le rôle
    await asyncio.sleep(604800)
    await membre.remove_roles(role_to_add_malus)
    await ctx.send(f"Le rôle {role_to_add_malus.mention} a été retiré de {membre.mention} après 1 semaine. ⏳")
#------------------------------------------------------------------------- Commandes d'économie : !!annihilation

@bot.command(name="annihilation")
async def annihilation(ctx, membre: discord.Member):
    """Ajoute le rôle 'Cible D'anéantissement' à un utilisateur si l'exécutant a le rôle 'Perm Crystal D'anéantissement'.
       Un embed est envoyé dans un salon spécifique (avec un ping) et l'exécutant perd son rôle 'Perm Crystal D'anéantissement'.
    """
    ROLE_REQUIRED = "″ [𝑺ץ] Perm Crystal D'anéantissement"  # Rôle requis pour exécuter la commande
    ROLE_TO_ADD = "″ [𝑺ץ] Cible D'anéantissement"  # Rôle à ajouter à la cible
    CHANNEL_ID = 1341844144032714833  # Salon spécial pour l'annonce
    ROLE_PING_ID = 792755123587645461  # ID à ping

    # Récupération des rôles et du salon
    role_required = discord.utils.get(ctx.guild.roles, name=ROLE_REQUIRED)
    role_to_add = discord.utils.get(ctx.guild.roles, name=ROLE_TO_ADD)
    channel = bot.get_channel(CHANNEL_ID)

    if not role_required or not role_to_add or not channel:
        return await ctx.send("❌ L'un des rôles ou le salon spécifié n'existe pas.")

    if role_required not in ctx.author.roles:
        return await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")

    # Ajouter le rôle à la cible et retirer le rôle de l'exécutant
    await membre.add_roles(role_to_add)
    await ctx.author.remove_roles(role_required)

    # Création de l'embed avec les informations demandées
    embed = discord.Embed(
        title="Annihilation",
        color=discord.Color.dark_red(),
        description="Un anéantissement a été effectué."
    )
    embed.add_field(name="Cibleur", value=ctx.author.mention, inline=True)
    embed.add_field(name="Cible", value=membre.mention, inline=True)
    embed.add_field(name="Rôle attribué", value=role_to_add.mention, inline=False)
    embed.set_footer(text="Annihilation exécutée")
    embed.timestamp = ctx.message.created_at

    # Envoi dans le salon spécial avec le ping au-dessus de l'embed
    ping = f"<@{ROLE_PING_ID}>"
    await channel.send(content=ping, embed=embed)

    # Confirmation dans le canal d'exécution de la commande
    await ctx.send(f"✅ {membre.mention} a été ciblé par un anéantissement. Le rôle {role_to_add.mention} a été attribué.")
#------------------------------------------------------------------------- Commandes d'économie : !!gravity

@bot.command(name="gravity")
async def gravity(ctx, membre: discord.Member):
    """Ajoute le rôle '″ [𝑺ץ] Gravité Forte' à un utilisateur, retire le rôle '″ [𝑺ץ] Perm Gravité Forte' de l'exécutant,
       et envoie un message confirmant l'opération.
       Seuls ceux ayant le rôle '″ [𝑺ץ] Perm Gravité Forte' peuvent utiliser cette commande.
    """
    ROLE_REQUIRED = "″ [𝑺ץ] Perm Gravité Forte"  # Rôle requis pour exécuter la commande
    ROLE_TO_ADD = "″ [𝑺ץ] Gravité Forte"  # Rôle à ajouter
    ROLE_TO_REMOVE = "″ [𝑺ץ] Perm Gravité Forte"  # Rôle à retirer à l'exécutant

    role_required = discord.utils.get(ctx.guild.roles, name=ROLE_REQUIRED)
    role_to_add = discord.utils.get(ctx.guild.roles, name=ROLE_TO_ADD)
    role_to_remove = discord.utils.get(ctx.guild.roles, name=ROLE_TO_REMOVE)

    if not role_required or not role_to_add or not role_to_remove:
        return await ctx.send("❌ L'un des rôles spécifiés n'existe pas.")

    if role_required not in ctx.author.roles:
        return await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")

    # Ajouter le rôle à la cible
    await membre.add_roles(role_to_add)
    await ctx.send(f"Le rôle {role_to_add.mention} a été ajouté à {membre.mention}. 🌌")

    # Retirer le rôle à l'exécutant
    if role_to_remove in ctx.author.roles:
        await ctx.author.remove_roles(role_to_remove)
        await ctx.send(f"Le rôle {role_to_remove.mention} vous a été retiré. ❌")
    else:
        await ctx.send(f"{ctx.author.mention}, vous n'aviez pas le rôle {role_to_remove.mention}. ❌")

#------------------------------------------------------------------------- Commandes d'économie : !!spatial

@bot.command(name="spatial")
async def spatial(ctx):
    """Ajoute temporairement le rôle '[𝑺ץ] Spatial' si l'utilisateur a '[𝑺ץ] Perm Spatial',
       et applique un cooldown de 24 heures. L'heure de la dernière utilisation est enregistrée dans la base de données MongoDB.
    """
    ROLE_REQUIRED = "″ [𝑺ץ] Perm Spatial"  # Rôle requis pour exécuter la commande
    ROLE_TO_ADD = "″ [𝑺ץ] Spatial"  # Rôle à ajouter temporairement
    COOLDOWN_DURATION = 86400  # 24 heures en secondes
    TEMP_ROLE_DURATION = 3600  # 1 heure en secondes

    role_required = discord.utils.get(ctx.guild.roles, name=ROLE_REQUIRED)
    role_to_add = discord.utils.get(ctx.guild.roles, name=ROLE_TO_ADD)

    if not role_required or not role_to_add:
        return await ctx.send("❌ L'un des rôles spécifiés n'existe pas.")

    if role_required not in ctx.author.roles:
        return await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")

    # Connexion à la base de données
    user_data = collection.find_one({"user_id": ctx.author.id})

    if user_data:
        last_used = user_data.get("last_used", 0)
    else:
        last_used = 0

    now = datetime.datetime.utcnow().timestamp()

    # Vérifier si l'utilisateur est en cooldown
    if now - last_used < COOLDOWN_DURATION:
        remaining_time = int((COOLDOWN_DURATION - (now - last_used)) / 3600)
        return await ctx.send(f"❌ Vous devez attendre encore {remaining_time} heure(s) avant de réutiliser cette commande.")

    # Ajouter le rôle temporaire
    await ctx.author.add_roles(role_to_add)
    await ctx.send(f"Le rôle {role_to_add.mention} vous a été attribué pour 1 heure. 🚀")

    # Mettre à jour l'heure de la dernière utilisation dans la base de données
    collection.update_one({"user_id": ctx.author.id}, {"$set": {"last_used": now}}, upsert=True)

    # Supprimer le rôle après 1 heure
    await asyncio.sleep(TEMP_ROLE_DURATION)
    await ctx.author.remove_roles(role_to_add)
    await ctx.send(f"Le rôle {role_to_add.mention} vous a été retiré après 1 heure. ⏳")

#------------------------------------------------------------------------- Commandes d'économie : !!heal

@bot.command(name="heal")
async def heal(ctx):
    """Supprime les rôles de malus et retire le rôle permettant d'utiliser la commande, avec un message en embed."""
    ROLE_REQUIRED = "″ [𝑺ץ] Perm Anti-Dote"  # Rôle requis pour exécuter la commande
    ROLE_TO_REMOVE_1 = "″ [𝑺ץ] Gravité Forte"  # Premier rôle à enlever
    ROLE_TO_REMOVE_2 = "″ [𝑺ץ] Malus Temporelle"  # Deuxième rôle à enlever

    role_required = discord.utils.get(ctx.guild.roles, name=ROLE_REQUIRED)
    role_to_remove_1 = discord.utils.get(ctx.guild.roles, name=ROLE_TO_REMOVE_1)
    role_to_remove_2 = discord.utils.get(ctx.guild.roles, name=ROLE_TO_REMOVE_2)

    if not role_required or not role_to_remove_1 or not role_to_remove_2:
        return await ctx.send("❌ L'un des rôles spécifiés n'existe pas.")

    if role_required not in ctx.author.roles:
        return await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")

    roles_removed = []

    # Vérifier et retirer les rôles si présents
    if role_to_remove_1 in ctx.author.roles:
        await ctx.author.remove_roles(role_to_remove_1)
        roles_removed.append(role_to_remove_1.mention)

    if role_to_remove_2 in ctx.author.roles:
        await ctx.author.remove_roles(role_to_remove_2)
        roles_removed.append(role_to_remove_2.mention)

    # Création de l'embed en fonction du nombre de rôles supprimés
    embed = discord.Embed(color=discord.Color.green())

    if len(roles_removed) == 2:
        embed.title = "✨ Guérison Complète"
        embed.description = f"{ctx.author.mention}, vous avez été totalement purgé de vos blessures et malédictions ! Plus rien ne vous entrave. 🏥"
        embed.add_field(name="Rôles retirés", value=", ".join(roles_removed), inline=False)

    elif len(roles_removed) == 1:
        embed.title = "🌿 Guérison Partielle"
        embed.description = f"{ctx.author.mention}, vous avez été guéri de **{roles_removed[0]}** ! Encore un petit effort pour être totalement rétabli. 💊"

    else:
        embed.title = "😂 Tentative de guérison échouée"
        embed.description = f"{ctx.author.mention}, tu essaies de te soigner alors que tu n'as rien ? T'es un clown !? 🤡"

    await ctx.send(embed=embed)

    # Retirer le rôle "Perm Anti-Dote" après l'utilisation
    await ctx.author.remove_roles(role_required)

    embed_removal = discord.Embed(
        title="🔻 Antidote consommé",
        description=f"{ctx.author.mention}, votre **{role_required.mention}** a été retiré après utilisation.",
        color=discord.Color.red()
    )
    await ctx.send(embed=embed_removal)
#------------------------------------------------------------------------- Commandes d'économie : !!protect

@bot.command(name="protect")
async def protect(ctx):
    """Ajoute temporairement le rôle '[𝑺ץ] Protect !!rob' si l'utilisateur a '[𝑺ץ] Perm Protect !!rob',
       et applique un cooldown de 48 heures.
    """
    ROLE_REQUIRED = "″ [𝑺ץ] Perm Protect !!rob"  # Rôle requis pour exécuter la commande
    ROLE_TO_ADD = "″ [𝑺ץ] Protect !!rob"  # Rôle à ajouter temporairement
    COOLDOWN_DURATION = 172800  # 48 heures en secondes
    TEMP_ROLE_DURATION = 172800  # 48 heures en secondes

    role_required = discord.utils.get(ctx.guild.roles, name=ROLE_REQUIRED)
    role_to_add = discord.utils.get(ctx.guild.roles, name=ROLE_TO_ADD)

    if not role_required or not role_to_add:
        return await ctx.send("❌ L'un des rôles spécifiés n'existe pas.")

    if role_required not in ctx.author.roles:
        return await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")

    now = datetime.datetime.utcnow().timestamp()

    # Vérifier si l'utilisateur est en cooldown dans la base de données
    user_data = collection.find_one({"user_id": ctx.author.id})

    if user_data:
        last_used = user_data.get("last_used", 0)
        time_since_last_use = now - last_used
        if time_since_last_use < COOLDOWN_DURATION:
            remaining_time = int((COOLDOWN_DURATION - time_since_last_use) / 3600)
            return await ctx.send(f"❌ Vous devez attendre encore {remaining_time} heure(s) avant de réutiliser cette commande.")
    else:
        # Si l'utilisateur n'a pas de données dans la base, l'ajouter
        collection.insert_one({"user_id": ctx.author.id, "last_used": now})

    # Ajouter le rôle temporaire
    await ctx.author.add_roles(role_to_add)
    await ctx.send(f"Le rôle {role_to_add.mention} vous a été attribué pour 2 jours. 🚀")

    # Mettre à jour l'heure d'utilisation dans la base de données
    collection.update_one({"user_id": ctx.author.id}, {"$set": {"last_used": now}}, upsert=True)

    # Supprimer le rôle après 48 heures
    await asyncio.sleep(TEMP_ROLE_DURATION)
    await ctx.author.remove_roles(role_to_add)
    await ctx.send(f"Le rôle {role_to_add.mention} vous a été retiré après 2 jours. ⏳")

#------------------------------------------------------------------------- Commandes d'économie : /embed

THUMBNAIL_URL = "https://github.com/Cass64/EtheryaBot/blob/main/images_etherya/etheryBot_profil.jpg?raw=true"

# Fonction pour vérifier si une URL est valide
def is_valid_url(url):
    regex = re.compile(
        r'^(https?://)?'  # http:// ou https:// (optionnel)
        r'([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}'  # domaine
        r'(/.*)?$'  # chemin (optionnel)
    )
    return bool(re.match(regex, url))

class EmbedBuilderView(discord.ui.View):
    def __init__(self, author: discord.User, channel: discord.TextChannel):
        super().__init__(timeout=180)
        self.author = author
        self.channel = channel
        self.embed = discord.Embed(title="Titre", description="Description", color=discord.Color.blue())
        self.embed.set_thumbnail(url=THUMBNAIL_URL)
        self.second_image_url = None
        self.message = None  # Stocke le message contenant l'embed

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.author:
            await interaction.response.send_message("❌ Vous ne pouvez pas modifier cet embed.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Modifier le titre", style=discord.ButtonStyle.primary)
    async def edit_title(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(EmbedTitleModal(self))

    @discord.ui.button(label="Modifier la description", style=discord.ButtonStyle.primary)
    async def edit_description(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(EmbedDescriptionModal(self))

    @discord.ui.button(label="Changer la couleur", style=discord.ButtonStyle.primary)
    async def edit_color(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.embed.color = discord.Color.random()
        if self.message:
            await self.message.edit(embed=self.embed, view=self)
        else:
            await interaction.response.send_message("Erreur : impossible de modifier le message.", ephemeral=True)

    @discord.ui.button(label="Ajouter une image", style=discord.ButtonStyle.secondary)
    async def add_image(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(EmbedImageModal(self))

    @discord.ui.button(label="Ajouter 2ème image", style=discord.ButtonStyle.secondary)
    async def add_second_image(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(EmbedSecondImageModal(self))

    @discord.ui.button(label="Envoyer", style=discord.ButtonStyle.success)
    async def send_embed(self, interaction: discord.Interaction, button: discord.ui.Button):
        embeds = [self.embed]
        if self.second_image_url:
            second_embed = discord.Embed(color=self.embed.color)
            second_embed.set_image(url=self.second_image_url)
            embeds.append(second_embed)

        await self.channel.send(embeds=embeds)
        await interaction.response.send_message("✅ Embed envoyé !", ephemeral=True)

class EmbedTitleModal(discord.ui.Modal):
    def __init__(self, view: EmbedBuilderView):
        super().__init__(title="Modifier le Titre")
        self.view = view
        self.title_input = discord.ui.TextInput(label="Nouveau Titre", required=True)
        self.add_item(self.title_input)

    async def on_submit(self, interaction: discord.Interaction):
        self.view.embed.title = self.title_input.value
        if self.view.message:
            await self.view.message.edit(embed=self.view.embed, view=self.view)
        else:
            await interaction.response.send_message("Erreur : impossible de modifier le message.", ephemeral=True)

class EmbedDescriptionModal(discord.ui.Modal):
    def __init__(self, view: EmbedBuilderView):
        super().__init__(title="Modifier la description")
        self.view = view
        self.description = discord.ui.TextInput(
            label="Nouvelle description",
            style=discord.TextStyle.paragraph,
            max_length=4000
        )
        self.add_item(self.description)

    async def on_submit(self, interaction: discord.Interaction):
        self.view.embed.description = self.description.value
        if self.view.message:
            await self.view.message.edit(embed=self.view.embed, view=self.view)
        else:
            await interaction.response.send_message("Erreur : impossible de modifier le message.", ephemeral=True)

class EmbedImageModal(discord.ui.Modal):
    def __init__(self, view: EmbedBuilderView):
        super().__init__(title="Ajouter une image")
        self.view = view
        self.image_input = discord.ui.TextInput(label="URL de l'image", required=False)
        self.add_item(self.image_input)

    async def on_submit(self, interaction: discord.Interaction):
        if self.image_input.value and is_valid_url(self.image_input.value):
            self.view.embed.set_image(url=self.image_input.value)
            if self.view.message:
                await self.view.message.edit(embed=self.view.embed, view=self.view)
            else:
                await interaction.response.send_message("Erreur : impossible de modifier le message.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ URL invalide.", ephemeral=True)

class EmbedSecondImageModal(discord.ui.Modal):
    def __init__(self, view: EmbedBuilderView):
        super().__init__(title="Ajouter une 2ème image")
        self.view = view
        self.second_image_input = discord.ui.TextInput(label="URL de la 2ème image", required=False)
        self.add_item(self.second_image_input)

    async def on_submit(self, interaction: discord.Interaction):
        if self.second_image_input.value and is_valid_url(self.second_image_input.value):
            self.view.second_image_url = self.second_image_input.value
            if self.view.message:
                await self.view.message.edit(embed=self.view.embed, view=self.view)
            else:
                await interaction.response.send_message("Erreur : impossible de modifier le message.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ URL invalide.", ephemeral=True)

@bot.tree.command(name="embed", description="Créer un embed personnalisé")
async def embed_builder(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    role_id = 1170326040485318686  # ID du rôle requis
    if not any(role.id == role_id for role in interaction.user.roles):
        return await interaction.response.send_message("❌ Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)

    view = EmbedBuilderView(interaction.user, interaction.channel)
    response = await interaction.followup.send(embed=view.embed, view=view, ephemeral=True)
    view.message = response  # Stocke le message contenant la View

@bot.event
async def on_message(message):
    if message.attachments:
        attachment = message.attachments[0]
        if attachment.content_type and attachment.content_type.startswith("image/"):
            embed = discord.Embed(title="Image ajoutée")
            embed.set_thumbnail(url=THUMBNAIL_URL)
            embed.set_image(url=attachment.url)
            await message.channel.send(embed=embed)

    await bot.process_commands(message)
#------------------------------------------------------------------------- Commandes classiques pour les prêt 


#------------------------------------------------------------------------- Commandes /frags

@bot.tree.command(name="frags")
async def frags(interaction: discord.Interaction, user: discord.Member):
    """Ajoute le rôle Frags Quotidien à un utilisateur pour 24 heures et enregistre l'expiration en base de données."""
    if not any(role.name == GF_REQUIRED_ROLE for role in interaction.user.roles):
        await interaction.response.send_message("❌ Tu n'as pas le rôle requis pour utiliser cette commande.", ephemeral=True)
        return

    FRAG_ROLE = "″ [𝑺ץ] Frags Quotidien"
    frag_role = discord.utils.get(interaction.guild.roles, name=FRAG_ROLE)

    if not frag_role:
        await interaction.response.send_message(f"❌ Le rôle `{FRAG_ROLE}` n'existe pas sur ce serveur.", ephemeral=True)
        return

    await user.add_roles(frag_role)
    expiration_time = datetime.utcnow() + timedelta(hours=24)

    # Enregistrer l'expiration en base de données
    collection.update_one(
        {"user_id": user.id},
        {"$set": {"expires_at": expiration_time}},
        upsert=True
    )

    await interaction.response.send_message(f"✅ {user.mention} a reçu le rôle `{FRAG_ROLE}` pour 24 heures.", ephemeral=True)

    # Envoi de l'embed dans le salon staff
    CHANNEL_ID = 1341671012109914173
    salon_staff = interaction.guild.get_channel(CHANNEL_ID)
    if salon_staff:
        embed = discord.Embed(title="Vente Frags Quotidien", color=discord.Color.blue())
        embed.add_field(name="Acheteur", value=interaction.user.mention, inline=True)
        embed.add_field(name="Vendeur", value=user.mention, inline=True)
        embed.set_footer(text="Frags vendus via la commande /frags")
        await salon_staff.send(embed=embed)

#------------------------------------------------------------------------- Commandes frags-time

@bot.tree.command(name="frags_time")
async def frags_timeleft(interaction: discord.Interaction, user: discord.Member):
    """Affiche le temps restant avant que le rôle Frags Quotidien soit retiré."""
    record = collection.find_one({"user_id": user.id})
    
    if not record or "expires_at" not in record:
        await interaction.response.send_message(f"❌ {user.mention} n'a pas de rôle Frags Quotidien actif.", ephemeral=True)
        return

    expiration = record["expires_at"]
    time_left = expiration - datetime.utcnow()

    if time_left.total_seconds() <= 0:
        await interaction.response.send_message(f"❌ {user.mention} n'a plus le rôle Frags Quotidien.", ephemeral=True)
        return

    hours, remainder = divmod(int(time_left.total_seconds()), 3600)
    minutes, _ = divmod(remainder, 60)

    embed = discord.Embed(
        title="⏳ Temps restant pour Frags Quotidien",
        description=f"{user.mention} perdra son rôle dans **{hours}h {minutes}m**.",
        color=discord.Color.green()
    )
    embed.set_footer(text="Ce rôle est temporaire, il sera retiré après 24 heures.")
    await interaction.response.send_message(embed=embed)

#------------------------------------------------------------------------- Commandes /pret


# Rôle requis pour certaines commandes
GF_REQUIRED_ROLE = "″ [𝑺ץ] Gestion & Finance Team"

# Dictionnaire pour stocker les prêts en cours (persistant dans MongoDB)
prets_en_cours = {}

# Commandes classiques avec préfixe qui nécessitent le rôle
@bot.command(name="pret10k")
async def pret10k(ctx, membre: discord.Member):
    """Enregistre un prêt de 10k avec détails dans un salon staff."""
    if not any(role.name == GF_REQUIRED_ROLE for role in ctx.author.roles):
        return await ctx.send("❌ Tu n'as pas le rôle requis pour utiliser cette commande.")
    await enregistrer_pret(ctx, membre, montant=10000, montant_rendu=11500, duree="1 Semaine")

@bot.command(name="pret25k")
async def pret25k(ctx, membre: discord.Member):
    """Enregistre un prêt de 25k avec détails dans un salon staff."""
    if not any(role.name == GF_REQUIRED_ROLE for role in ctx.author.roles):
        return await ctx.send("❌ Tu n'as pas le rôle requis pour utiliser cette commande.")
    await enregistrer_pret(ctx, membre, montant=25000, montant_rendu=28750, duree="1 Semaine")

@bot.command(name="pret50k")
async def pret50k(ctx, membre: discord.Member):
    """Enregistre un prêt de 50k avec détails dans un salon staff."""
    if not any(role.name == GF_REQUIRED_ROLE for role in ctx.author.roles):
        return await ctx.send("❌ Tu n'as pas le rôle requis pour utiliser cette commande.")
    await enregistrer_pret(ctx, membre, montant=50000, montant_rendu=57500, duree="1 Semaine")

async def enregistrer_pret(ctx, membre, montant, montant_rendu, duree):
    """Enregistre un prêt avec détails et envoie un message dans le salon staff."""
    CHANNEL_ID = 1340674704964583455  # Remplacez par l'ID du salon staff
    salon_staff = bot.get_channel(CHANNEL_ID)

    if not salon_staff:
        return await ctx.send("❌ Le salon staff n'a pas été trouvé.")

    embed = discord.Embed(title="📜 Nouveau Prêt", color=discord.Color.blue())
    embed.add_field(name="👤 Pseudonyme", value=membre.mention, inline=True)
    embed.add_field(name="💰 Montant demandé", value=f"{montant:,} crédits", inline=True)
    embed.add_field(name="📄 Ticket/Formulaire", value="Ticket", inline=True)
    embed.add_field(name="📅 Date pour rendre", value=duree, inline=True)
    embed.add_field(name="💳 Montant à rendre", value=f"{montant_rendu:,} crédits", inline=True)
    embed.add_field(name="🔄 Statut", value="En Cours", inline=True)
    embed.set_footer(text=f"Prêt enregistré par {ctx.author.display_name}")

    # Sauvegarde du prêt dans MongoDB
    prets_en_cours[membre.id] = {"montant": montant, "montant_rendu": montant_rendu, "statut": "En Cours"}
    collection.update_one({"user_id": membre.id}, {"$set": {"pret": prets_en_cours[membre.id]}}, upsert=True)

    await salon_staff.send(embed=embed)
    await ctx.send(f"✅ Prêt de {montant:,} crédits accordé à {membre.mention}. Détails envoyés aux staff.")

@bot.command(name="terminer")
async def terminer(ctx, membre: discord.Member):
    """Marque un prêt comme 'Payé' si l'utilisateur avait un prêt en cours."""
    CHANNEL_ID = 1340674704964583455  # ID du salon staff
    salon_staff = bot.get_channel(CHANNEL_ID)

    if not salon_staff:
        return await ctx.send("❌ Le salon staff n'a pas été trouvé.")

    # Vérifier si l'utilisateur a un prêt en cours dans la base de données
    user_data = collection.find_one({"user_id": membre.id})
    if not user_data or "pret" not in user_data:
        return await ctx.send(f"❌ {membre.mention} n'a aucun prêt en cours.")

    # Récupération des détails du prêt
    pret = user_data["pret"]
    montant = pret["montant"]
    montant_rendu = pret["montant_rendu"]

    # Création de l'embed pour confirmer le remboursement
    embed = discord.Embed(title="✅ Prêt Remboursé", color=discord.Color.green())
    embed.add_field(name="👤 Pseudonyme", value=membre.mention, inline=True)
    embed.add_field(name="💰 Montant demandé", value=f"{montant:,} crédits", inline=True)
    embed.add_field(name="📄 Ticket/Formulaire", value="Ticket", inline=True)
    embed.add_field(name="💳 Montant remboursé", value=f"{montant_rendu:,} crédits", inline=True)
    embed.add_field(name="🔄 Statut", value="Payé", inline=True)
    embed.set_footer(text=f"Prêt remboursé confirmé par {ctx.author.display_name}")

    # Mettre à jour le statut du prêt dans la base de données
    pret["statut"] = "Payé"
    collection.update_one({"user_id": membre.id}, {"$set": {"pret": pret}})

    await salon_staff.send(embed=embed)
    await ctx.send(f"✅ Le prêt de {montant:,} crédits de {membre.mention} est marqué comme remboursé.")

    # Envoi d'un MP au membre
    try:
        await membre.send(f"✅ Bonjour {membre.mention}, ton prêt de **{montant:,} crédits** a bien été remboursé. "
                          f"Le statut de ton prêt a été mis à jour comme **Payé**.")
    except discord.Forbidden:
        await ctx.send(f"❌ Impossible d'envoyer un MP à {membre.mention}, il a désactivé les messages privés.")  

@bot.tree.command(name="pret")
@app_commands.describe(
    membre="Le membre à qui le prêt est accordé",
    montant="Le montant du prêt",
    montant_à_rendre="Le montant à rendre",
    duree="La durée du prêt",
    methode="Méthode utilisée : Ticket ou Formulaire"
)
async def pret(interaction: discord.Interaction, membre: discord.Member, montant: int, montant_à_rendre: int, duree: str, methode: str):
    """Enregistre un prêt avec les détails dans un salon staff."""
    if methode.lower() not in ["ticket", "formulaire"]:
        await interaction.response.send_message("❌ Méthode invalide. Choisis entre `Ticket` ou `Formulaire`.", ephemeral=True)
        return

    if not any(role.name == GF_REQUIRED_ROLE for role in interaction.user.roles):
        await interaction.response.send_message("❌ Tu n'as pas le rôle requis pour utiliser cette commande.", ephemeral=True)
        return

    # Appel de la fonction pour enregistrer le prêt
    await enregistrer_pret(interaction, membre, montant, montant_à_rendre, duree, methode.capitalize())

async def enregistrer_pret(interaction: discord.Interaction, membre: discord.Member, montant: int, montant_à_rendre: int, duree: str, methode: str):
    """Enregistre un prêt avec détails et envoie un message dans le salon staff."""
    CHANNEL_ID = 1340674704964583455  # ID du salon staff
    salon_staff = interaction.guild.get_channel(CHANNEL_ID)

    if not salon_staff:
        return await interaction.response.send_message("❌ Le salon staff n'a pas été trouvé.", ephemeral=True)

    embed = discord.Embed(title="📜 Nouveau Prêt", color=discord.Color.blue())
    embed.add_field(name="👤 Pseudonyme", value=membre.mention, inline=True)
    embed.add_field(name="💰 Montant demandé", value=f"{montant:,} crédits", inline=True)
    embed.add_field(name="📄 Méthode", value=methode, inline=True)
    embed.add_field(name="📅 Date pour rendre", value=duree, inline=True)
    embed.add_field(name="💳 Montant à rendre", value=f"{montant_à_rendre:,} crédits", inline=True)
    embed.add_field(name="🔄 Statut", value="En Cours", inline=True)
    embed.set_footer(text=f"Prêt enregistré par {interaction.user.display_name}")  # Utilisation correcte de `interaction.user`

    # Sauvegarde du prêt dans MongoDB
    prets_en_cours[membre.id] = {
        "montant": montant, 
        "montant_rendu": montant_à_rendre, 
        "methode": methode, 
        "statut": "En Cours"
    }
    collection.update_one({"user_id": membre.id}, {"$set": {"pret": prets_en_cours[membre.id]}}, upsert=True)

    await salon_staff.send(embed=embed)
    await interaction.response.send_message(f"✅ Prêt de {montant:,} crédits accordé à {membre.mention} avec la méthode `{methode}`. Détails envoyés aux staff.")


@bot.tree.command(name="pretpayer")
async def pretpayer(interaction: discord.Interaction, membre: discord.Member):
    """Marque un prêt comme 'Payé' si l'utilisateur avait un prêt en cours."""
    if not any(role.name == GF_REQUIRED_ROLE for role in interaction.user.roles):
        await interaction.response.send_message("❌ Tu n'as pas le rôle requis pour utiliser cette commande.", ephemeral=True)
        return

    CHANNEL_ID = 1340674730683924593  # ID du salon staff
    salon_staff = interaction.guild.get_channel(CHANNEL_ID)

    if not salon_staff:
        return await interaction.response.send_message("❌ Le salon staff n'a pas été trouvé.", ephemeral=True)

    # Vérifier si l'utilisateur a un prêt en cours dans la base de données
    user_data = collection.find_one({"user_id": membre.id})
    if not user_data or "pret" not in user_data:
         return await interaction.response.send_message(f"❌ {membre.mention} n'a pas de prêt en cours.", ephemeral=True)

  # Récupération des détails du prêt
    pret = user_data["pret"]
    montant = pret["montant"]
    montant_rendu = pret["montant_rendu"]

    # Création de l'embed pour confirmer le remboursement
    embed = discord.Embed(title="✅ Prêt Remboursé", color=discord.Color.green())
    embed.add_field(name="👤 Pseudonyme", value=membre.mention, inline=True)
    embed.add_field(name="💰 Montant demandé", value=f"{montant:,} crédits", inline=True)
    embed.add_field(name="📄 Méthode", value=pret.get("methode", "Non spécifiée"), inline=True)
    embed.add_field(name="💳 Montant remboursé", value=f"{montant_rendu:,} crédits", inline=True)
    embed.add_field(name="🔄 Statut", value="Payé", inline=True)
    embed.set_footer(text=f"Prêt remboursé confirmé par {interaction.user.display_name}")

    # Mettre à jour le statut du prêt dans la base de données
    pret["statut"] = "Payé"
    collection.update_one({"user_id": membre.id}, {"$set": {"pret": pret}})

    await salon_staff.send(embed=embed)
    await interaction.response.send_message(f"✅ Le prêt de {montant:,} crédits de {membre.mention} est marqué comme remboursé.")

    # Envoi d'un MP au membre
    try:
        await membre.send(f"✅ Bonjour {membre.mention}, ton prêt de **{montant:,} crédits** a bien été remboursé. "
                          f"Le statut de ton prêt a été mis à jour comme **Payé**.")
    except discord.Forbidden:
        await interaction.response.send_message(f"❌ Impossible d'envoyer un MP à {membre.mention}, il a désactivé les messages privés.", ephemeral=True)

#------------------------------------------------------------------------- Commandes de Livret A
@bot.tree.command(name="investirlivreta")  # Tout en minuscules
@app_commands.describe(montant="Somme à investir (max 100,000)")
async def investir_livret(interaction: discord.Interaction, montant: int):
    """Investit une somme dans le Livret A (max 100k)"""

    # Déférer la réponse pour éviter l'erreur "Interaction has already been acknowledged"
    await interaction.response.defer(thinking=True)  

    if montant <= 0 or montant > 100_000:
        await interaction.followup.send("❌ Tu dois investir entre **1 et 100,000** 💰.", ephemeral=True)
        return

    user_id = interaction.user.id
    user_data = collection.find_one({"user_id": user_id})

    ancien_montant = user_data["livretA"] if user_data and "livretA" in user_data else 0
    nouveau_montant = ancien_montant + montant

    collection.update_one(
        {"user_id": user_id},
        {"$set": {"livretA": nouveau_montant}},
        upsert=True
    )

    # ID du salon et du rôle à ping
    CHANNEL_ID = 1343687225790959647  # Remplace par l'ID du salon
    ROLE_ID = 1341494709184368734  # Remplace par l'ID du rôle 
    salon = interaction.guild.get_channel(CHANNEL_ID)
    role_ping = f"<@&{ROLE_ID}>"  # Ping du rôle

    embed = discord.Embed(
        title="📥 Investissement - Livret A",
        description=f"{interaction.user.mention} a investi **{montant}** 💰 dans son Livret A !\n💰 Total : **{nouveau_montant}**",
        color=discord.Color.green()
    )

    if salon:
        await salon.send(content=role_ping, embed=embed)
    
    # Utiliser `followup.send()` car `response.send_message()` ne peut plus être utilisé
    await interaction.followup.send(
        f"✅ Tu as investi **{montant}** 💰 dans ton Livret A ! (Total: {nouveau_montant} 💰) "
        f"💡 Cela peut prendre quelques heures avant que l'argent soit ajouté à ton livret.",
        ephemeral=True
    )

#---------------------------------------------------------------

@bot.tree.command(name="livreta")
async def consulter_livret(interaction: discord.Interaction):
    """Affiche la somme actuelle dans le Livret A de l'utilisateur."""
    await interaction.response.defer(ephemeral=True)

    user_id = interaction.user.id
    record = collection.find_one({"user_id": user_id})

    if not record or "livretA" not in record:
        await interaction.followup.send("💰 Vous n'avez pas encore investi dans un Livret A.", ephemeral=True)
        return

    montant = record["livretA"]
    embed = discord.Embed(
        title="📈 Solde du Livret A",
        description=f"💰 Votre solde actuel : **{montant}** crédits",
        color=discord.Color.green()
    )
    embed.set_footer(text="Les intérêts sont ajoutés chaque semaine (+2%).")
    
    await interaction.followup.send(embed=embed, ephemeral=True)

#---------------------------------------------------------------

@bot.tree.command(name="retirerlivreta")  # Tout en minuscules
@app_commands.describe(montant="Somme à retirer (laisser vide pour tout retirer)")
async def retirer_livret(interaction: discord.Interaction, montant: int = None):
    """Retire une somme du Livret A et notifie un salon."""
    user_id = interaction.user.id
    user_data = collection.find_one({"user_id": user_id})

    if not user_data or "livretA" not in user_data or user_data["livretA"] == 0:
        await interaction.response.send_message("❌ Tu n'as pas d'argent dans ton Livret A.", ephemeral=True)
        return
    
    montant_max = user_data["livretA"]
    montant = montant if montant is not None else montant_max

    if montant <= 0 or montant > montant_max:
        await interaction.response.send_message(f"❌ Tu peux retirer entre **1 et {montant_max}** 💰.", ephemeral=True)
        return

    collection.update_one(
        {"user_id": user_id},
        {"$inc": {"livretA": -montant}}
    )

    # ID du salon et du rôle 
    CHANNEL_ID =  1343674317053104349 # Remplace par l'ID du salon
    ROLE_ID = 1341494709184368734  # Remplace par l'ID du rôle
    salon = interaction.guild.get_channel(CHANNEL_ID)
    role_ping = f"<@&{ROLE_ID}>"  # Ping du rôle

    embed = discord.Embed(
        title="💸 Demande de Retrait - Livret A",
        description=f"{interaction.user.mention} souhaite retirer **{montant}** 💰 de son Livret A.",
        color=discord.Color.orange()
    )
    embed.set_footer(text="Un administrateur doit valider cette demande.")

    if salon:
        await salon.send(content=role_ping, embed=embed)
    
    await interaction.response.send_message(f"✅ Tu as demandé à retirer **{montant}** 💰 de ton Livret A ! Cela peut prendre quelques heure avant que ton argent te soit ajouter à ton compte.", ephemeral=True)

#---------------------------------------------------------------

@aiocron.crontab("0 0 * * 0")  # Tous les dimanches à 00:00 UTC
async def ajouter_interets():
    """Ajoute 2% d'intérêts sur le Livret A chaque dimanche à minuit."""
    utilisateurs = collection.find({"livretA": {"$gt": 0}})
    for user in utilisateurs:
        user_id = user["user_id"]
        montant = user["livretA"]
        nouveaux_interets = math.floor(montant * 0.02)  # 2% d'intérêt arrondi

        collection.update_one(
            {"user_id": user_id},
            {"$inc": {"livretA": nouveaux_interets}}
        )

        print(f"✅ Intérêts ajoutés : {user_id} a gagné {nouveaux_interets} 💰")

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

from datetime import datetime, timedelta
import discord
import random
from discord import app_commands
from discord.ext import commands
from discord.utils import get

# Définition des rôles et du cooldown
PERM_CONSTRUCTION_ROLE = "″ [𝑺ץ] Perm Construction"
ENTREPRENEUR_ROLE = "″ [𝑺ץ] Entrepreneur"
ANNOUNCE_CHANNEL_ID = 1343698434653159424  # ID du salon d'annonce
STAFF_USER_ID = 1343719454298869780
COOLDOWN_TIME = timedelta(hours=12)

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Commande pour construire une entreprise
@bot.tree.command(name="constructionentreprise", description="Construire une entreprise")
@app_commands.describe(nom="Choisissez le nom de votre entreprise")
async def construction_entreprise(interaction: discord.Interaction, nom: str):
    user = interaction.user
    guild = interaction.guild

    role = get(guild.roles, name=PERM_CONSTRUCTION_ROLE)

    if not role or role not in user.roles:
        return await interaction.response.send_message(
            "❌ Vous n'avez pas la permission de construire une entreprise.", ephemeral=True
        )

    # Vérifier si l'utilisateur a déjà une entreprise
    user_data = collection.find_one({"user_id": user.id})
    if user_data and user_data.get("entreprise_constructed", False):
        return await interaction.response.send_message(
            "❌ Vous avez déjà une entreprise en activité. Utilisez `/quitterentreprise` pour en créer une autre.", ephemeral=True
        )

    # Donne le rôle "Entrepreneur" à l'utilisateur
    entrepreneur_role = get(guild.roles, name=ENTREPRENEUR_ROLE)
    if entrepreneur_role:
        await user.add_roles(entrepreneur_role)

    # Enregistre l'entreprise et le cooldown si existant
    collection.update_one(
        {"user_id": user.id},
        {
            "$set": {
                "entreprise_constructed": True,
                "nom_entreprise": nom,
            },
            "$setOnInsert": {
                "last_collect_time": None  # Garde le cooldown existant s'il y en avait un
            }
        },
        upsert=True
    )

    # Embed pour le joueur
    embed_user = discord.Embed(
        title="🏗️ Construction d'Entreprise",
        description=f"{user.mention}, vous avez construit **{nom}** avec succès ! 🎉",
        color=discord.Color.green()
    )
    embed_user.set_footer(text="Bonne chance avec votre nouvelle entreprise !")

    await interaction.response.send_message(embed=embed_user, ephemeral=True)

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Commande pour collecter les revenus de l'entreprise
@bot.tree.command(name="collectentreprise", description="Collecter les revenus de votre entreprise")
async def collect_entreprise(interaction: discord.Interaction):
    user = interaction.user
    guild = interaction.guild

    role = get(guild.roles, name=ENTREPRENEUR_ROLE)

    if not role or role not in user.roles:
        return await interaction.response.send_message(
            "❌ Vous devez être un entrepreneur pour collecter des revenus.", ephemeral=True
        )

    # Vérification du cooldown et récupération du nom de l'entreprise
    user_data = collection.find_one({"user_id": user.id})
    last_time = user_data.get("last_collect_time", None)
    nom_entreprise = user_data.get("nom_entreprise", "Votre entreprise")

    now = datetime.utcnow()

    if last_time and now - last_time < COOLDOWN_TIME:
        remaining_time = COOLDOWN_TIME - (now - last_time)
        hours, remainder = divmod(int(remaining_time.total_seconds()), 3600)
        minutes = remainder // 60
        return await interaction.response.send_message(
            f"⏳ Vous devez attendre encore {hours}h {minutes}m avant de collecter à nouveau.", ephemeral=True
        )

    # Génération d'un montant aléatoire entre 25,000 et 50,000
    amount = random.randint(25000, 50000)

    # Mise à jour du cooldown uniquement, l'argent sera envoyé plus tard
    collection.update_one(
        {"user_id": user.id},
        {"$set": {"last_collect_time": now}},
        upsert=True
    )

    # Embed de gain
    embed_gain = discord.Embed(
        title="💰 Revenus d'Entreprise",
        description=f"{user.mention}, votre entreprise **{nom_entreprise}** a généré des revenus.\n"
                    f"Vous recevrez **{amount:,}** pièces dans les prochaines heures. 🏦",
        color=discord.Color.gold()
    )
    embed_gain.set_footer(text="L'argent sera ajouté plus tard sur votre compte.")

    await interaction.response.send_message(embed=embed_gain, ephemeral=True)

    # Message dans le salon d'annonce avec un ping spécifique
    announce_channel = bot.get_channel(ANNOUNCE_CHANNEL_ID)
    if announce_channel:
        staff_user = guild.get_member(STAFF_USER_ID)
        if staff_user:
            await announce_channel.send(f"{staff_user.mention}") 

        embed_announce = discord.Embed(
            title="📢 Revenus d'Entreprise en attente",
            description=f"{user.mention} a généré **{amount:,}** pièces avec **{nom_entreprise}**.\n"
                        f"Le paiement sera traité sous peu. 💰",
            color=discord.Color.blue()
        )
        embed_announce.set_footer(text="Surveillez les paiements.")
        await announce_channel.send(embed=embed_announce)

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Commande pour quitter l'entreprise
@bot.tree.command(name="quitterentreprise", description="Quitter ou supprimer votre entreprise")
async def quitter_entreprise(interaction: discord.Interaction):
    user = interaction.user
    guild = interaction.guild

    role = get(guild.roles, name=ENTREPRENEUR_ROLE)

    if not role or role not in user.roles:
        return await interaction.response.send_message(
            "❌ Vous devez être un entrepreneur pour quitter une entreprise.", ephemeral=True
        )

    # Vérifie si l'utilisateur a une entreprise construite
    user_data = collection.find_one({"user_id": user.id})
    if not user_data or not user_data.get("entreprise_constructed", False):
        return await interaction.response.send_message(
            "❌ Vous n'avez pas d'entreprise à quitter.", ephemeral=True
        )

    # Retirer le rôle Entrepreneur
    await user.remove_roles(role)

    # Supprimer l'entreprise mais garder le cooldown
    collection.update_one(
        {"user_id": user.id},
        {"$set": {"entreprise_constructed": False, "nom_entreprise": None}},
        upsert=True
    )

    # Embed de confirmation pour l'utilisateur
    embed_user = discord.Embed(
        title="🚫 Quitter l'Entreprise",
        description=f"{user.mention}, vous avez quitté votre entreprise.\n"
                    "Votre historique de collecte reste enregistré.",
        color=discord.Color.red()
    )
    embed_user.set_footer(text="Vous pouvez reconstruire une entreprise plus tard.")

    await interaction.response.send_message(embed=embed_user, ephemeral=True)

#------------------------------------------------------------------------- calcul

@bot.tree.command(name="calcul", description="Calcule un pourcentage d'un nombre")
@app_commands.describe(nombre="Le nombre de base", pourcentage="Le pourcentage à appliquer (ex: 15 pour 15%)")
async def calcul(interaction: discord.Interaction, nombre: float, pourcentage: float):
    await interaction.response.defer()  # ✅ Correctement placé à l'intérieur de la fonction

    resultat = (nombre * pourcentage) / 100
    embed = discord.Embed(
        title="📊 Calcul de pourcentage",
        description=f"{pourcentage}% de {nombre} = **{resultat}**",
        color=discord.Color.green()
    )

    await interaction.followup.send(embed=embed)
    
#------------------------------------------------------------------------- ECONOMIEW ------------------------------------------------------------------------- ECONOMIE------------------------------------------------------------------------- ECONOMIE------------------------------------------------------------------------- ECONOMIE-------
#------------------------------------------------------------------------- ECONOMIEW ------------------------------------------------------------------------- ECONOMIE------------------------------------------------------------------------- ECONOMIE------------------------------------------------------------------------- ECONOMIE-------
#------------------------------------------------------------------------- ECONOMIEW ------------------------------------------------------------------------- ECONOMIE------------------------------------------------------------------------- ECONOMIE------------------------------------------------------------------------- ECONOMIE-------
#------------------------------------------------------------------------- ECONOMIEW ------------------------------------------------------------------------- ECONOMIE------------------------------------------------------------------------- ECONOMIE------------------------------------------------------------------------- ECONOMIE-------

# Rôle autorisé pour les commandes économiques
allowed_role_eco = "″ [𝑺ץ] Développeur"  # Remplace par le nom de ton rôle spécifique
special_role = "*"  # Rôle supplémentaire pour les commandes spéciales

# Fonction pour créer un embed personnalisé
def create_embed(title, description):
    embed = discord.Embed(title=title, description=description, color=discord.Color.green())
    return embed

# Fonction pour vérifier les permissions
def has_permission_eco(ctx):
    return any(role.name == allowed_role_eco for role in ctx.author.roles)

def has_permission_special(ctx):
    return any(role.name == special_role for role in ctx.author.roles) and has_permission_eco(ctx)

# Commande pour ajouter de l'argent à un utilisateur
@bot.command(name="add_money")
async def add_money(ctx, user: discord.Member, amount: int):
    if not has_permission_special(ctx):
        await ctx.send(embed=create_embed("Permission refusée", "Tu n'as pas la permission d'utiliser cette commande."))
        return

    collection2.update_one({"user_id": user.id}, {"$inc": {"balance": amount}}, upsert=True)
    await ctx.send(embed=create_embed("Ajout d'argent", f"{amount} crédits ont été ajoutés à {user.name}."))

# Commande pour retirer de l'argent à un utilisateur
@bot.command(name="remove_money")
async def remove_money(ctx, user: discord.Member, amount: int):
    if not has_permission_special(ctx):
        await ctx.send(embed=create_embed("Permission refusée", "Tu n'as pas la permission d'utiliser cette commande."))
        return

    collection2.update_one({"user_id": user.id}, {"$inc": {"balance": -amount}}, upsert=True)
    await ctx.send(embed=create_embed("Retrait d'argent", f"{amount} crédits ont été retirés à {user.name}."))

# Commande pour afficher l'argent d'un utilisateur
@bot.command(name="balance")
async def balance(ctx, user: discord.Member = None):
    user = user or ctx.author
    data = collection2.find_one({"user_id": user.id})

    if data and "balance" in data:
        await ctx.send(embed=create_embed(f"Solde de {user.name}", f"{user.name} a {data['balance']} crédits."))
    else:
        await ctx.send(embed=create_embed(f"Solde de {user.name}", f"{user.name} n'a pas de solde enregistré."))

# Commande de dépôt (only with /)
@bot.tree.command(name="deposit")
async def deposit(ctx, amount: int):
    if not has_permission_eco(ctx):
        await ctx.send(embed=create_embed("Permission refusée", "Tu n'as pas la permission d'utiliser cette commande."))
        return

    # Exemple de dépôt d'argent
    collection2.update_one({"user_id": ctx.author.id}, {"$inc": {"balance": amount}}, upsert=True)
    await ctx.send(embed=create_embed("Dépôt réussi", f"{amount} crédits ont été déposés sur ton compte."))

# Commande de retrait (only with /)
@bot.tree.command(name="withdraw")
async def withdraw(ctx, amount: int):
    if not has_permission_eco(ctx):
        await ctx.send(embed=create_embed("Permission refusée", "Tu n'as pas la permission d'utiliser cette commande."))
        return

    # Exemple de retrait d'argent
    collection2.update_one({"user_id": ctx.author.id}, {"$inc": {"balance": -amount}}, upsert=True)
    await ctx.send(embed=create_embed("Retrait réussi", f"{amount} crédits ont été retirés de ton compte."))

# Commande de transfert (only with /)
@bot.tree.command(name="transfer")
async def transfer(ctx, user: discord.Member, amount: int):
    if not has_permission_eco(ctx):
        await ctx.send(embed=create_embed("Permission refusée", "Tu n'as pas la permission d'utiliser cette commande."))
        return

    # Exemple de transfert d'argent
    collection2.update_one({"user_id": ctx.author.id}, {"$inc": {"balance": -amount}}, upsert=True)
    collection2.update_one({"user_id": user.id}, {"$inc": {"balance": amount}}, upsert=True)
    await ctx.send(embed=create_embed("Transfert réussi", f"{amount} crédits ont été transférés à {user.name}."))

# Commande pour acheter un item du store (only with /)
@bot.tree.command(name="buy")
async def buy(ctx, item_name: str):
    if not has_permission_eco(ctx):
        await ctx.send(embed=create_embed("Permission refusée", "Tu n'as pas la permission d'utiliser cette commande."))
        return

    item = collection2.find_one({"item_name": item_name})
    if item and item["stock"] > 0:
        user_data = collection2.find_one({"user_id": ctx.author.id})
        price = item["price"]
        if user_data["balance"] >= price:
            collection2.update_one({"user_id": ctx.author.id}, {"$inc": {"balance": -price, f"inventory.{item_name}": 1}}, upsert=True)
            collection2.update_one({"item_name": item_name}, {"$inc": {"stock": -1}})
            await ctx.send(embed=create_embed("Achat réussi", f"Tu as acheté {item_name} pour {price} crédits."))
        else:
            await ctx.send(embed=create_embed("Crédits insuffisants", "Tu n'as pas assez de crédits pour acheter cet item."))
    else:
        await ctx.send(embed=create_embed("Item introuvable", f"L'item {item_name} n'existe pas ou est en rupture de stock."))

# Commande pour afficher les items dans le store (only with /)
@bot.tree.command(name="store")
async def store(ctx):
    store_items = collection2.find({"item_name": {"$exists": True}})
    if store_items:
        items_list = "\n".join([f"{item['item_name']} - {item['price']} crédits - Stock: {item['stock']}" for item in store_items])
        await ctx.send(embed=create_embed("Store", items_list))
    else:
        await ctx.send(embed=create_embed("Store vide", "Il n'y a actuellement aucun item en vente."))

# Commande pour afficher l'inventaire (only with /)
@bot.tree.command(name="inventory")
async def inventory(ctx):
    user_data = collection2.find_one({"user_id": ctx.author.id})
    if user_data and "inventory" in user_data:
        inventory_list = "\n".join([f"{item}: {quantity}" for item, quantity in user_data["inventory"].items()])
        await ctx.send(embed=create_embed("Inventaire", f"Voici ton inventaire:\n{inventory_list}"))
    else:
        await ctx.send(embed=create_embed("Inventaire vide", "Tu n'as aucun item dans ton inventaire."))

# Commande .helpE pour afficher un embed d'aide sur les commandes économiques
@bot.command(name="helpE")
async def helpE(ctx):
    if not has_permission_eco(ctx):
        await ctx.send(embed=create_embed("Permission refusée", "Tu n'as pas la permission d'utiliser cette commande."))
        return

    embed = discord.Embed(
        title="🪙 Commandes économiques - Aide",
        description="Voici une liste des commandes économiques disponibles pour le moment. **Ces commandes sont à but de test et ne remplaceront pas le bot économique actuel.**",
        color=discord.Color(0x00FF00)  # Utilise une couleur verte pour un thème économique
    )

    embed.add_field(name="💸 `.balance`", value="Affiche ton solde actuel sur le serveur.", inline=False)
    embed.add_field(name="💰 `/deposit <montant>`", value="Dépose de l'argent sur ton compte.", inline=False)
    embed.add_field(name="🏧 `/withdraw <montant>`", value="Retire de l'argent de ton compte.", inline=False)
    embed.add_field(name="🔄 `/transfer <utilisateur> <montant>`", value="Transfère de l'argent à un autre utilisateur.", inline=False)
    embed.add_field(name="📦 `/inventory`", value="Affiche ton inventaire.", inline=False)
    embed.add_field(name="🛒 `/buy <item>`", value="Achète des objets de ton inventaire.", inline=False)
    embed.add_field(name="🛍 `/store`", value="Affiche les items en vente.", inline=False)

    embed.set_thumbnail(url="https://github.com/Cass64/EtheryaBot/blob/main/images_etherya/etheryaBot_profil.jpg?raw=true")
    embed.set_footer(text="Utilise ces commandes avec sagesse ! 💡")
    embed.set_image(url="https://github.com/Cass64/EtheryaBot/blob/main/images_etherya/etheryaBot_banniere.png?raw=true")

    await ctx.send(embed=embed)



#------------------------------------------------------------------------- Ignorer les messages des autres bots
@bot.event
async def on_message(message):
    # Ignorer les messages envoyés par d'autres bots
    if message.author.bot:
        return

    # Vérifie si le message mentionne uniquement le bot
    if bot.user.mentioned_in(message) and message.content.strip().startswith(f"<@{bot.user.id}>"):
        embed = discord.Embed(
            title="📜 Liste des Commandes",
            description="Voici la liste des commandes disponibles :",
            color=discord.Color(0xFFFFFF)
        )

        # Assure-toi de récupérer les objets de rôle pour pouvoir les mentionner
        role_gravity = discord.utils.get(message.guild.roles, name="″ [𝑺ץ] Gravité Forte")
        role_spatial = discord.utils.get(message.guild.roles, name="″ [𝑺ץ] Spatial")

        # Ajout des commandes
        embed.add_field(
            name="💥 .break <membre>",
            value="Retire un rôle spécifique à un membre. Exemple : .break @Utilisateur",
            inline=False
        )
        embed.add_field(
            name="⏳ .malus <membre>",
            value="Ajoute un rôle malus à un membre pour une durée prédéfinie de 24 heures. Exemple : .malus @Utilisateur",
            inline=False
        )
        embed.add_field(
            name="☠️ .annihilation <membre>",
            value="Cible un membre pour l'anéantissement. Exemple : .annihilation @Utilisateur",
            inline=False
        )
        embed.add_field(
            name="🌌 .gravity <membre>",
            value=f"Ajoute le rôle {role_gravity.mention} à un membre. Exemple : .gravity @Utilisateur",  # Mention du rôle ici
            inline=False
        )
        embed.add_field(
            name="🚀 .spatial <membre>",
            value=f"Ajoute temporairement le rôle {role_spatial.mention} à un membre. Exemple : .spatial @Utilisateur",  # Mention du rôle ici
            inline=False
        )
        embed.add_field(
            name="🏥 .heal",
            value="Retire les malus et soigne l'utilisateur exécutant la commande.",
            inline=False
        )
        embed.add_field(
            name="🛡️ .protect",
            value="Protège temporairement l'utilisateur des vols. Exemple : .protect",
            inline=False
        )
        
        # Commandes liées au Livret A
        embed.add_field(
            name="💸 /investirlivreta <montant>",
            value="Investit une somme dans le Livret A (max 100k). Exemple : .investirlivreta 1000",
            inline=False
        )
        embed.add_field(
            name="📈 /livreta",
            value="Affiche le solde actuel de ton Livret A.",
            inline=False
        )
        embed.add_field(
            name="💰 /retirerlivreta <montant>",
            value="Retire une somme de ton Livret A. Exemple : /retirerlivreta 500",
            inline=False
        )

        # Commandes liées à l'entreprise
        embed.add_field(
            name="🏗️ /constructionentreprise",
            value="Construis une entreprise (avec le rôle nécessaire). Exemple : /constructionentreprise",
            inline=False
        )
        embed.add_field(
            name="💼 /collectentreprise",
            value="Collecte les revenus de ton entreprise. Exemple : /collectentreprise",
            inline=False
        )
        embed.add_field(
            name="🚶‍♂️ /quitterentreprise",
            value="Quitte ou supprime ton entreprise. Exemple : /quitterentreprise",
            inline=False
        )

        embed.set_thumbnail(url="https://github.com/Cass64/EtheryaBot/blob/main/images_etherya/etheryBot_profil.jpg?raw=true")
        embed.set_footer(text="Utilise ces commandes avec sagesse !")
        embed.set_image(url="https://github.com/Cass64/EtheryaBot/blob/main/images_etherya/etheryaBot_banniere.png?raw=true")

        await message.channel.send(embed=embed)

    # Assurez-vous que le bot continue de traiter les commandes
    await bot.process_commands(message)
#------------------------------------------------------------------------- auto clan

#------------------------------------------------------------------------- Lancement du bot
keep_alive()
bot.run(token)
