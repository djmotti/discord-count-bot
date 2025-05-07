import os
import datetime
import discord
import aiohttp
from discord.ext import commands
from zoneinfo import ZoneInfo

# מאוכסן ב-Secrets של GitHub
WEBHOOK_URL = os.environ['DISCORD_WEBHOOK_URL']
BOT_TOKEN   = os.environ['DISCORD_BOT_TOKEN']

# שם הערוץ שמממנו נספור (עדכן לשם התעלה שלך)
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

    # מוצאים את הערוץ לפי שם
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

    # תאריך היום ושם היום בשבוע לפי שעון ישראל
    now       = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
    weekday_map = {
        1: "שני",
        2: "שלישי",
        3: "רביעי",
        4: "חמישי",
        5: "שישי",
        6: "שבת",
        7: "ראשון"
    }
    weekday   = weekday_map[now.isoweekday()]
    date_str  = now.strftime("%d.%m.%y")

    content = f"היום {weekday} {date_str} היו: {unique_visits} כניסות ו{new_downloads} הורדות."

    # שליחת ההודעה ישירות ל־Webhook URL
    async with aiohttp.ClientSession() as session:
        await session.post(WEBHOOK_URL, json={"content": content})

    await bot.close()

@bot.event
async def on_ready():
    await count_and_report()

if __name__ == "__main__":
    bot.run(BOT_TOKEN)
