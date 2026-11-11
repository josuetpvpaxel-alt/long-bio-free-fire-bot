import discord
from discord.ext import commands
import asyncio
from datetime import datetime
import os
from dotenv import load_dotenv
import aiohttp
from aiohttp import web

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
API_URL = "http://bio.thg4ff.xyz/update_bio"
KEY = "great"
PORT = int(os.getenv("PORT", 5000))

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

session = None
cooldowns = {}

REGIONS = {
    "ID": ("Indonesia", "🇮🇩"),
    "TH": ("Thailand", "🇹🇭"),
    "IND": ("India", "🇮🇳"),
    "BR": ("Brazil", "🇧🇷"),
    "SG": ("Singapore", "🇸🇬"),
    "BD": ("Bangladesh", "🇧🇩"),
    "PK": ("Pakistan", "🇵🇰"),
    "US": ("United States", "🇺🇸"),
    "MY": ("Malaysia", "🇲🇾"),
    "VN": ("Vietnam", "🇻🇳"),
    "EUROPE": ("Europe", "🇪🇺"),
    "RU": ("Russia", "🇷🇺"),
}

def format_region(code: str):
    code = code.upper()
    if code in REGIONS:
        name, flag = REGIONS[code]
        return f"{flag} {name}"
    return code

@bot.event
async def on_ready():
    global session
    if session is None:
        session = aiohttp.ClientSession()
    print(f"Logged in as {bot.user}")

@bot.command(name="bio")
async def bio(ctx, access_token: str = None, *, bio: str = None):
    if not access_token or not bio:
        return await ctx.reply(
            "**Usa:**\n`!bio <access_token> <new bio>`\n\n"
            "**Ejemplo:**\n`!bio ORVEX /python main.py!`"
        )

    now = datetime.now().timestamp()
    last = cooldowns.get(ctx.author.id, 0)
    if now - last < 30:
        return await ctx.send(
            f"⏳ Por favor espera!! **{int(30 - (now - last))}s** before reusing this command.",
            delete_after=6
        )
    cooldowns[ctx.author.id] = now

    try:
        await ctx.message.delete()
    except:
        pass

    await ctx.send("⏳ Actualizando biografía, espera un momento", delete_after=3)

    url = f"{API_URL}?access_token={access_token}&bio={bio}&key={KEY}"

    try:
        async with session.get(url) as resp:
            if resp.status != 200:
                return await ctx.send("❌ API error.", delete_after=6)
            data = await resp.json()

        if data.get("status") == "error":
            return await ctx.send("❌ Invalid or expired token.", delete_after=6)

        region = format_region(data.get("region", "UNK"))

        embed = discord.Embed(
            title="✅ Biografía Actualizada!",
            color=0x77d5a3,
            description=(
                f"> **Nombre:** {data.get('nickname', 'Unknown')}\n"
                f"> **Plataforma:** {data.get('platform', 'Unknown')}\n"
                f"> **Region:** {region}\n"
                f"> **UID:** {data.get('uid', 'Unknown')}\n"
                f"> **Biografía:** ||{data.get('bio', '')}||"
            )
        )
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        embed.set_footer(text="DEVELOPED BY Axel XIT")
        await ctx.send(ctx.author.mention, embed=embed)

    except Exception as e:
        print(e)
        await ctx.send("❌ Unexpected error.", delete_after=6)

async def start_web_server():
    app = web.Application()
    async def handle(request):
        return web.Response(text="Bot Está funcionando / Está en ejecución ✅")
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    print(f"Web server running on port {PORT}")

async def main():
    await start_web_server()
    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
