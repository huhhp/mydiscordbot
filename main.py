import discord
from discord.ext import commands
import wavelink
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot Online as {bot.user}")
    await wavelink.NodePool.create_node(
        bot=bot,
        host='lavalink.eu.org',
        port=2333,
        password='youshallnotpass',
        https=False
    )

@bot.command()
async def play(ctx, *, search: str):
    if not ctx.author.voice:
        await ctx.send("เข้าห้องเสียงก่อนนะครับ")
        return
    channel = ctx.author.voice.channel
    if not ctx.voice_client:
        vc: wavelink.Player = await channel.connect(cls=wavelink.Player)
    else:
        vc: wavelink.Player = ctx.voice_client
    results = await wavelink.Playable.search(search)
    if not results:
        await ctx.send("หาเพลงไม่เจอ ลองชื่ออื่นดูนะ!")
        return
    track = results[0]
    await vc.play(track)
    await ctx.send(f"🎵 Playing: {track.title}")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("⏹️ หยุดเพลงแล้ว")

bot.run(os.getenv("DISCORD_TOKEN"))