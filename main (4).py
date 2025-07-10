import os
import json
import random
import discord
from discord.ext import commands
import wavelink

TOKEN = os.getenv("TOKEN")
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
            host='lavalink.darrennathanael.com',
            port=2333,
            password='youshallnotpass',
            https=False
        )
        print("Connected to Lavalink!")
    except Exception as e:
        print(f"Lavalink connection error: {e}")

# ---------- 1. Music Commands ----------
@bot.command()
async def join(ctx):
    if ctx.author.voice:
        try:
            await ctx.author.voice.channel.connect(cls=wavelink.Player)
            await ctx.send(f"Joined {ctx.author.voice.channel.name}")
        except Exception as e:
            await ctx.send(f"Error joining voice channel: {e}")
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
    # ตรวจสอบว่ามี Lavalink node เชื่อมต่อหรือไม่
    if not wavelink.NodePool.nodes:
        await ctx.send("❌ ไม่มี Lavalink node เชื่อมต่อ! กรุณารอสักครู่...")
        return

    vc: wavelink.Player = ctx.voice_client
    if not vc:
        if ctx.author.voice:
            try:
                vc = await ctx.author.voice.channel.connect(cls=wavelink.Player)
                await ctx.send(f"🔗 เชื่อมต่อกับ {ctx.author.voice.channel.name}")
            except Exception as e:
                await ctx.send(f"❌ ไม่สามารถเข้าห้องเสียงได้: {e}")
                return
        else:
            await ctx.send("❌ คุณต้องเข้าห้องเสียงก่อน!")
            return

    try:
        tracks = await wavelink.YouTubeTrack.search(search)
        if not tracks:
            await ctx.send("❌ ไม่พบเพลงที่ค้นหา!")
            return

        track = tracks[0]
        await vc.play(track)

        embed = discord.Embed(
            title="🎵 กำลังเล่น",
            description=f"**{track.title}**",
            color=discord.Color.green()
        )
        if hasattr(track, 'author'):
            embed.add_field(name="ศิลปิน", value=track.author, inline=True)
        if hasattr(track, 'duration'):
            minutes, seconds = divmod(track.duration // 1000, 60)
            embed.add_field(name="ความยาว", value=f"{minutes:02d}:{seconds:02d}", inline=True)

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"❌ เกิดข้อผิดพลาด: {e}")
        print(f"Play error: {e}")

@bot.command()
async def stop(ctx):
    vc: wavelink.Player = ctx.voice_client
    if not vc:
        await ctx.send("Not in a voice channel.")
        return
    await vc.stop()
    await ctx.send("Stopped.")

@bot.command()
async def pause(ctx):
    vc: wavelink.Player = ctx.voice_client
    if not vc:
        await ctx.send("Not in a voice channel.")
        return
    await vc.pause(True)
    await ctx.send("Paused.")

@bot.command()
async def resume(ctx):
    vc: wavelink.Player = ctx.voice_client
    if not vc:
        await ctx.send("Not in a voice channel.")
        return
    await vc.pause(False)
    await ctx.send("Resumed.")

@bot.command()
async def skip(ctx):
    vc: wavelink.Player = ctx.voice_client
    if not vc:
        await ctx.send("Not in a voice channel.")
        return
    await vc.skip()
    await ctx.send("Skipped.")

# ---------- 2. AI Chat ----------
@bot.command()
async def ai(ctx, *, question=None):
    RESPONSES = [
        "วันนี้เป็นไงบ้างเอ่ย 😊", "สู้ๆ นะ!", "มีอะไรให้ช่วยก็บอกได้เลย",
        "ขอบคุณที่คุยกับฉัน!", "รักทุกคนในเซิร์ฟนี้เสมอ!", "พร้อมพัฒนาไปกับคุณ!",
        "วันนี้มีอะไรใหม่ๆ บ้างไหม?", "ฟังเพลงกันเถอะ!", "อยากให้ช่วยอะไรไหม?",
        "หวังว่าทุกคนจะมีความสุขนะ", "มาคุยกันได้เสมอเลย!"
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
    level = xp // 100
    await ctx.send(f"{user.display_name} มี XP: {xp} | Level: {level}")

@bot.command()
async def leaderboard(ctx):
    rank = load_rank()
    if not rank:
        await ctx.send("ยังไม่มีข้อมูล XP ของใครเลย!")
        return

    sorted_users = sorted(rank.items(), key=lambda x: x[1], reverse=True)[:10]
    leaderboard_text = "🏆 **Leaderboard Top 10** 🏆\n"

    for i, (user_id, xp) in enumerate(sorted_users, 1):
        try:
            user = bot.get_user(int(user_id))
            name = user.display_name if user else f"User {user_id}"
            level = xp // 100
            leaderboard_text += f"{i}. {name} - XP: {xp} | Level: {level}\n"
        except:
            continue

    await ctx.send(leaderboard_text)

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
    if message.content == last and len(message.content) > 5:
        await message.delete()
        await message.channel.send(f"{message.author.mention} อย่าสแปมข้อความซ้ำเกินไปนะ!", delete_after=5)
    else:
        last_message[channel_id][user_id] = message.content
        # Auto XP system
        rank = load_rank()
        uid = str(user_id)
        rank[uid] = rank.get(uid, 0) + 1
        save_rank(rank)

        await bot.process_commands(message)

# ---------- 5. Emoji Decorate ----------
@bot.command()
async def emoji(ctx, *, msg: str):
    EMOJIS = ["✨", "🔥", "💎", "🌈", "🎉", "⭐", "🌟", "💫", "🎊", "🎈"]
    result = f"{random.choice(EMOJIS)} {msg} {random.choice(EMOJIS)}"
    await ctx.send(result)

# ---------- 6. Announce ----------
@bot.command()
async def announce(ctx, *, msg: str):
    embed = discord.Embed(
        title="📢 ประกาศสำคัญ",
        description=msg,
        color=discord.Color.gold()
    )
    embed.set_footer(text=f"ประกาศโดย {ctx.author.display_name}")
    await ctx.send(embed=embed)

# ---------- 7. Custom Room & Roles ----------
@bot.command()
async def create_private(ctx, name: str):
    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }
    try:
        channel = await ctx.guild.create_text_channel(name, overwrites=overwrites)
        await channel.send(f"🏠 ห้องส่วนตัวสำหรับ {ctx.author.mention}! พิมพ์ `!delete_private` เพื่อลบห้องนี้")
        await ctx.send(f"สร้างห้องส่วนตัว {channel.mention} เรียบร้อยแล้ว!")
    except Exception as e:
        await ctx.send(f"ไม่สามารถสร้างห้องได้: {e}")

@bot.command()
async def delete_private(ctx):
    if ctx.channel.name.startswith(ctx.author.name.lower()) or ctx.author.guild_permissions.manage_channels:
        await ctx.channel.delete()
    else:
        await ctx.send("คุณไม่มีสิทธิ์ลบห้องนี้!")

@bot.command()
async def giverole(ctx, member: discord.Member, *, role_name: str):
    try:
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if not role:
            role = await ctx.guild.create_role(name=role_name, colour=discord.Colour.random())
        await member.add_roles(role)
        await ctx.send(f"✅ {member.mention} ได้รับยศ **{role.name}** แล้ว!")
    except Exception as e:
        await ctx.send(f"ไม่สามารถให้ยศได้: {e}")

# ---------- 8. Log ----------
@bot.event
async def on_command(ctx):
    print(f"[LOG] Command: {ctx.command} by {ctx.author} in {ctx.channel}")
    try:
        with open("self_improve.log", "a", encoding="utf-8") as f:
            f.write(f"{ctx.author} used {ctx.command} in {ctx.channel}\n")
    except Exception as e:
        print(f"Log error: {e}")

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
        "ใส่ระบบความปลอดภัย/ตรวจจับบัญชีใหม่/auto-ban",
        "เพิ่มระบบ queue เพลง และ playlist",
        "สร้างระบบ economy และ shop",
        "เพิ่มระบบ moderation อัตโนมัติ"
    ]
    embed = discord.Embed(
        title="🧠 AI Suggestion",
        description=random.choice(suggestions),
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

# ---------- 10. Pin Help ----------
@bot.command()
async def pinhelp(ctx):
    embed = discord.Embed(
        title="🎉 คู่มือใช้งานบอทในเซิร์ฟเวอร์นี้ 🎉",
        color=discord.Color.green()
    )
    embed.add_field(
        name="🎵 คำสั่งเพลง",
        value="!join / !leave - เข้า/ออกห้องเสียง\n!play [ชื่อเพลง] - เปิดเพลง\n!stop - หยุดเพลง\n!pause / !resume - หยุด/เล่นต่อ\n!skip - ข้ามเพลง",
        inline=False
    )
    embed.add_field(
        name="🤖 AI & ระบบ",
        value="!ai [ข้อความ] - คุยกับ AI\n!upgrade_ai - ขอข้อเสนอใหม่",
        inline=False
    )
    embed.add_field(
        name="🏆 ระบบ XP/Rank",
        value="!addxp @user [จำนวน] - เพิ่ม XP\n!rank - ดู XP ตัวเอง\n!leaderboard - ดู top 10",
        inline=False
    )
    embed.add_field(
        name="👑 จัดการเซิร์ฟเวอร์",
        value="!giverole @user [ยศ] - แจกยศ\n!create_private [ชื่อห้อง] - สร้างห้องส่วนตัว\n!delete_private - ลบห้องส่วนตัว\n!announce [ข้อความ] - ประกาศ\n!emoji [ข้อความ] - ตกแต่งข้อความ",
        inline=False
    )

    msg_obj = await ctx.send(embed=embed)
    try:
        await msg_obj.pin()
    except:
        pass

# ---------- Fun Commands ----------
@bot.command()
async def dice(ctx, sides: int = 6):
    if sides < 2 or sides > 100:
        await ctx.send("จำนวนหน้าต้องอยู่ระหว่าง 2-100!")
        return
    result = random.randint(1, sides)
    await ctx.send(f"🎲 ทอยลูกเต้า {sides} หน้า ได้: **{result}**")

@bot.command()
async def coin(ctx):
    result = random.choice(["หัว", "ก้อย"])
    emoji = "🪙" if result == "หัว" else "⚡"
    await ctx.send(f"{emoji} เหรียญออก: **{result}**")

@bot.command()
async def lavalink_status(ctx):
    """ตรวจสอบสถานะ Lavalink server"""
    if not wavelink.NodePool.nodes:
        await ctx.send("❌ ไม่มี Lavalink server เชื่อมต่อ")
        return

    embed = discord.Embed(
        title="📊 Lavalink Node Status",
        color=discord.Color.blue()
    )

    for node in wavelink.NodePool.nodes.values():
        status_emoji = "🟢" if node.is_connected() else "🔴"
        status_text = "Connected" if node.is_connected() else "Disconnected"

        embed.add_field(
            name=f"{status_emoji} {node.identifier}",
            value=f"Status: {status_text}\nPlayers: {len(node.players)}",
            inline=True
        )

    await ctx.send(embed=embed)

try:
    if TOKEN == "" or TOKEN is None:
        raise Exception("Please add your token to the Secrets pane.")
    bot.run(TOKEN)
except discord.HTTPException as e:
    if e.status == 429:
        print("The Discord servers denied the connection for making too many requests")
        print("Get help from https://stackoverflow.com/questions/66724687/in-discord-py-how-to-solve-the-error-for-toomanyrequests")
    else:
        raise e