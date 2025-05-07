import os
import re
import datetime
import discord
from discord.ext import commands

# מאוכסן ב-Secrets של GitHub
WEBHOOK_URL = os.environ['DISCORD_WEBHOOK_URL']
BOT_TOKEN   = os.environ['DISCORD_BOT_TOKEN']

intents = discord.Intents.default()
intents.messages = True
intents.guilds   = True

bot = commands.Bot(command_prefix='!', intents=intents)

async def count_and_report():
    # מוציאים את מזהה ה-Webhook מה-URL
    m = re.match(r'https?://discord\.com/api/webhooks/(\d+)/[\w-]+', WEBHOOK_URL)
    if not m:
        print("Invalid webhook URL")
        await bot.close()
        return

    webhook_id = int(m.group(1))
    # מושכים את ה-Webhook כדי לקבל את channel_id
    webhook = await bot.fetch_webhook(webhook_id)
    channel = bot.get_channel(webhook.channel_id)

    # מחשבים 24 שעות אחורה
    since = datetime.datetime.utcnow() - datetime.timedelta(days=1)

    visits = 0
    downloads = 0

    async for msg in channel.history(after=since):
        txt = msg.content.lower()
        if 'הורדה' in txt or 'download' in txt:
            downloads += 1
        elif 'כניסה' in txt or 'visit' in txt:
            visits += 1

    # שולחים את הסיכום לאותו ערוץ
    await channel.send(
        f"**ספירה יומית (24h):**\n› כניסות: {visits}\n› הורדות: {downloads}"
    )
    await bot.close()

@bot.event
async def on_ready():
    await count_and_report()

if __name__ == "__main__":
    bot.run(BOT_TOKEN)
