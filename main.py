import os
import datetime
import discord
import aiohttp
from discord.ext import commands
from zoneinfo import ZoneInfo

# מאוכסן ב-Secrets של GitHub
WEBHOOK_URL = os.environ['DISCORD_WEBHOOK_URL']
BOT_TOKEN   = os.environ['DISCORD_BOT_TOKEN']

# שם הערוץ ממנו נספור (תעדכן לשם התעלה שלך)
CHANNEL_NAME = "resu-me"

# הגדרת intents, כולל Message Content Intent
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds   = True

bot = commands.Bot(command_prefix='!', intents=intents)

async def count_and_report():
    # מחשבים 24 שעות אחורה ב-UTC
    since = datetime.datetime.utcnow() - datetime.timedelta(days=1)

    unique_visits = 0
    new_downloads = 0

    # מוצאים את הערוץ לפי השם
    channel = next(
        (c for c in bot.get_all_channels() if c.name.lower() == CHANNEL_NAME),
        None
    )

    if channel:
        async for msg in channel.history(after=since):
            txt = msg.content.lower()
            if 'הורדה חדשה' in txt:
                new_downloads += 1
            elif 'כניסה ייחודית' in txt:
                unique_visits += 1
    else:
        print(f"Channel '{CHANNEL_NAME}' not found – aborting count.")

    # תאריך היום לפי שעון ישראל
    now      = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
    date_str = now.strftime("%d.%m.%y")
    content  = f"היום ה{date_str} היו: {unique_visits} כניסות ו{new_downloads} הורדות."

    # שליחת ההודעה ישירות ל־WEBHOOK_URL
    async with aiohttp.ClientSession() as session:
        await session.post(WEBHOOK_URL, json={"content": content})

    await bot.close()

@bot.event
async def on_ready():
    await count_and_report()

if __name__ == "__main__":
    bot.run(BOT_TOKEN)
