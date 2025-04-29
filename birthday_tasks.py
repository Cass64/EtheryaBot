from discord.ext import tasks
from datetime import datetime
import discord

from utils.database import get_profiles_collection
from start import bot  # Assure-toi que `bot` est bien importé depuis ton instance principale

@tasks.loop(time=datetime.strptime("08:00", "%H:%M").time())  # Tous les jours à 08h
async def check_birthdays():
    print("🔍 Vérification des anniversaires en cours...")
    collection = get_profiles_collection()
    today = datetime.utcnow()
    day = today.day
    month = today.month
    year = today.year

    async for profil in collection.find({"anniversaire": {"$exists": True}}):
        anniversaire = profil.get("anniversaire")
        user_id = profil["_id"]
        last_check_year = profil.get("last_birthday_check")

        try:
            if not anniversaire or anniversaire.lower() == "non renseigné":
                continue

            # Format attendu : DD/MM/YYYY
            parts = anniversaire.split("/")
            if len(parts) != 3:
                continue

            d, m, y = map(int, parts)
            if d == day and m == month and str(year) != str(last_check_year):
                channel_id = 1355230266163204200
                channel = bot.get_channel(channel_id)
                if not channel:
                    continue

                # Envoi de l'embed anniversaire
                embed = discord.Embed(
                    title="🎉 Joyeux anniversaire ! 🎉",
                    description=f"Souhaitez un joyeux anniversaire à <@{user_id}> ! 🥳",
                    color=discord.Color.magenta(),
                    timestamp=today
                )
                embed.set_image(url="https://media.giphy.com/media/3o6Zt481isNVuQI1l6/giphy.gif")
                embed.set_footer(text="De la part de toute la communauté 🎁")
                await channel.send(embed=embed)

                # Marquer l'anniversaire comme célébré pour cette année
                await collection.update_one(
                    {"_id": user_id},
                    {"$set": {"last_birthday_check": year}}
                )
        except Exception as e:
            print(f"❌ Erreur lors de la vérification d'anniversaire pour l'utilisateur {user_id} : {e}")
