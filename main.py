import os
import re
import datetime
import discord
import aiohttp
from discord import Webhook
from discord.webhook import AsyncWebhookAdapter
from discord.ext import commands
from zoneinfo import ZoneInfo

# מאוכסן ב-Secrets של GitHub
WEBHOOK_URL = os.environ['DISCORD_WEBHOOK_URL']
BOT_TOKEN   = os.environ['DISCORD_BOT_TOKEN']

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

    # ספירת ההודעות מהערוץ עליו עובד ה-BotUser
    # נניח שאתם רוצים לקרוא מערוץ בשם 'resu-me'
    channel = discord.utils.get(bot.get_all_channels(), name="resu-me")
    if channel:
        async for msg in channel.history(after=since):
            txt = msg.content.lower()
            if 'הורדה חדשה' in txt:
                new_downloads += 1
            elif 'כניסה ייחודית' in txt:
                unique_visits += 1

    # תאריך היום לפי שעון ישראל
    now      = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
    date_str = now.strftime("%d.%m.%y")
    content  = f"היום ה{date_str} היו: {unique_visits} כניסות ו{new_downloads} הורדות."

    # שליחת ההודעה דרך ה-Webhook בלי הרשאות נוספות
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(WEBHOOK_URL, adapter=AsyncWebhookAdapter(session))
        await webhook.send(content)

    await bot.close()

@bot.event
async def on_ready():
    await count_and_report()

if __name__ == "__main__":
    bot.run(BOT_TOKEN)
