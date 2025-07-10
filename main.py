import os
import json
import random
import discord
from discord.ext import commands
import wavelink

TOKEN = os.getenv("DISCORD_TOKEN")
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

RANK_FILE = "rank.json"
if not os.path.exists(RANK_FILE):
    with open(RANK_FILE, "w") as f:
        json.dump({}, f)

def load_rank():
    with open(RANK_FILE, "r") as f:
        return json.load(f)

def save_rank(rank):
    with open(RANK_FILE, "w") as f:
        json.dump(rank, f)

# ---------- Music Node Setup ----------
@bot.event
async def on_ready():
    print(f"Bot {bot.user} is ready!")
    try:
        await wavelink.NodePool.create_node(
            bot=bot,
            host='lavalink.eu.org',
            port=2333,
            password='youshallnotpass',
            https=False
        )
    except Exception as e:
        print(f"Lavalink connection error: {e}")

# ---------- 1. Music Commands ----------
@bot.command()
async def join(ctx):
    if ctx.author.voice:
        await ctx.author.voice.channel.connect(cls=wavelink.Player)
        await ctx.send(f"Joined {ctx.author.voice.channel.name}")
    else:
        await ctx.send("Join a voice channel first!")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected!")
    else:
        await ctx.send("Not connected to a voice channel.")

@bot.command()
async def play(ctx, *, search: str):
    vc: wavelink.Player = ctx.voice_client
    if not vc:
        if ctx.author.voice:
            vc = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        else:
            await ctx.send("You must be in a voice channel!")
            return
    tracks = await wavelink.YouTubeTrack.search(search)
    if not tracks:
        await ctx.send("No results found!")
        return
    track = tracks[0]
    await vc.play(track)
    await ctx.send(f"Now playing: {track.title}")

@bot.command()
async def stop(ctx):
    vc: wavelink.Player = ctx.voice_client
    if not vc:
        await ctx.send("Not in a voice channel.")
        return
    await vc.stop()
    await ctx.send("Stopped.")

# ---------- 2. AI Chat ----------
@bot.command()
async def ai(ctx, *, question=None):
    RESPONSES = [
        "วันนี้เป็นไงบ้างเอ่ย 😊", "สู้ๆ นะ!", "มีอะไรให้ช่วยก็บอกได้เลย",
        "ขอบคุณที่คุยกับฉัน!", "รักทุกคนในเซิร์ฟนี้เสมอ!", "พร้อมพัฒนาไปกับคุณ!"
    ]
    if not question:
        await ctx.send("ถามหรือปรึกษาอะไรก็ได้เลย~")
    else:
        await ctx.send(random.choice(RESPONSES))

# ---------- 3. Rank/Level ----------
@bot.command()
async def addxp(ctx, user: discord.Member, xp: int):
    rank = load_rank()
    uid = str(user.id)
    rank[uid] = rank.get(uid, 0) + xp
    save_rank(rank)
    await ctx.send(f"{user.display_name} ได้รับ XP เพิ่ม {xp}!")

@bot.command()
async def rank(ctx, user: discord.Member = None):
    rank = load_rank()
    user = user or ctx.author
    uid = str(user.id)
    xp = rank.get(uid, 0)
    await ctx.send(f"{user.display_name} มี XP {xp}")

# ---------- 4. Anti-Spam ----------
last_message = {}
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    channel_id = message.channel.id
    user_id = message.author.id
    if channel_id not in last_message:
        last_message[channel_id] = {}
    last = last_message[channel_id].get(user_id, "")
    if message.content == last:
        await message.delete()
        await message.channel.send(f"{message.author.mention} อย่าสแปมข้อความซ้ำเกินไปนะ!")
    else:
        last_message[channel_id][user_id] = message.content
        await bot.process_commands(message)

# ---------- 5. Emoji Decorate ----------
@bot.command()
async def emoji(ctx, *, msg: str):
    EMOJIS = ["✨", "🔥", "💎", "🌈", "🎉"]
    result = f"{random.choice(EMOJIS)} {msg} {random.choice(EMOJIS)}"
    await ctx.send(result)

# ---------- 6. Announce ----------
@bot.command()
async def announce(ctx, *, msg: str):
    await ctx.send(f"📢 **ประกาศ:** {msg}")

# ---------- 7. Custom Room & Roles ----------
@bot.command()
async def create_private(ctx, name: str):
    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        ctx.author: discord.PermissionOverwrite(read_messages=True)
    }
    channel = await ctx.guild.create_text_channel(name, overwrites=overwrites)
    await channel.send(f"ห้องนี้สำหรับ {ctx.author.mention}!")

@bot.command()
async def giverole(ctx, member: discord.Member, *, role_name: str):
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if not role:
        role = await ctx.guild.create_role(name=role_name, colour=discord.Colour.random())
    await member.add_roles(role)
    await ctx.send(f"{member.mention} ได้รับยศ {role.name} แล้ว!")

# ---------- 8. Log ----------
@bot.event
async def on_command(ctx):
    print(f"[LOG] Command: {ctx.command} by {ctx.author} in {ctx.channel}")
    with open("self_improve.log", "a") as f:
        f.write(f"{ctx.author} used {ctx.command} in {ctx.channel}
")

# ---------- 9. Self-Upgrade ----------
@bot.command()
async def upgrade_ai(ctx):
    suggestions = [
        "ควรเพิ่ม mini-game หรือระบบกิจกรรมในเซิร์ฟ",
        "เพิ่มโมดูล AI Chat ภาษาไทย-อังกฤษ (แปล/ถามตอบอัตโนมัติ)",
        "สร้างระบบแจ้งเตือน event, schedule หรือ countdown",
        "พัฒนาระบบ anti-spam ให้ฉลาดขึ้น เช่น ใช้ AI จับ pattern ข้อความ",
        "เก็บ log การใช้งานแบบสรุปรายเดือน/รายสัปดาห์",
        "เชื่อมกับฐานข้อมูลหรือระบบความจำระยะยาว",
        "ใส่ระบบความปลอดภัย/ตรวจจับบัญชีใหม่/auto-ban"
    ]
    await ctx.send("🧠 **AI Suggestion:** " + random.choice(suggestions))

# ---------- 10. Pin Help ----------
@bot.command()
async def pinhelp(ctx):
    msg = (
        "**🎉 คู่มือใช้งานบอทในเซิร์ฟเวอร์นี้ 🎉**\n"
        "- !join / !leave : ให้บอทเข้า-ออกห้องเสียง\n"
        "- !play [ชื่อเพลงหรือ url] : เปิดเพลง\n"
        "- !stop : หยุดเพลง\n"
        "- !ai [ข้อความ] : คุยกับ AI\n"
        "- !addxp @user 10 : เพิ่ม XP ให้เพื่อน\n"
        "- !rank : ดู XP ตัวเอง\n"
        "- !giverole @user ชื่อยศ : รับ/แจกยศ\n"
        "- !create_private [ชื่อห้อง] : สร้างห้องส่วนตัว\n"
        "- !announce ข้อความ : ประกาศข่าว\n"
        "- !emoji ข้อความ : ตกแต่งข้อความ\n"
        "- !upgrade_ai : ขอข้อเสนอใหม่ ๆ จาก AI"
    )
    msg_obj = await ctx.send(msg)
    await msg_obj.pin()

bot.run(TOKEN)