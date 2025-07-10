
# Discord Music Bot (Python + wavelink)

โปรเจกต์นี้เป็น Discord Bot ที่มีความสามารถด้านเพลงและระบบจัดการเซิร์ฟเวอร์

## ฟีเจอร์หลัก

- 🎵 **ระบบเพลง**: เปิดเพลงจาก YouTube ด้วย wavelink
- 🤖 **AI Chat**: คุยกับบอท AI ภาษาไทย
- 🏆 **ระบบ XP/Rank**: เพิ่ม XP ให้สมาชิก
- 🛡️ **Anti-Spam**: ป้องกันการส่งข้อความซ้ำ
- 👑 **จัดการยศ**: สร้างและแจกยศใหม่
- 🏠 **ห้องส่วนตัว**: สร้างห้องแชทส่วนตัว
- 📢 **ประกาศ**: ระบบประกาศข่าวสาร
- ✨ **ตกแต่งข้อความ**: เพิ่ม emoji ให้ข้อความ

## วิธีใช้งาน

### สำหรับ Replit
1. สร้าง Bot ที่ [Discord Developer Portal](https://discord.com/developers/applications)
2. เพิ่ม TOKEN ใน Secrets ด้วยชื่อ `TOKEN`
3. กด Run เพื่อเริ่มใช้งาน

### สำหรับ Render (Deploy 24/7)
1. Fork repository นี้ไปยัง GitHub
2. เข้า [Render.com](https://render.com) และ Connect GitHub
3. สร้าง Web Service ใหม่
4. เลือก repository ที่ fork มา
5. ตั้งค่า:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
6. เพิ่ม Environment Variable:
   - `TOKEN` = Discord Bot Token ของคุณ
7. กด Deploy

### สำหรับ Local Development
```bash
git clone <your-repo-url>
cd discord-music-bot
pip install -r requirements.txt
export TOKEN="your_discord_token_here"
python main.py
```

## คำสั่งหลัก

- `!join` / `!leave` - เข้า/ออกห้องเสียง
- `!play [ชื่อเพลง]` - เปิดเพลง
- `!stop` - หยุดเพลง
- `!ai [ข้อความ]` - คุยกับ AI
- `!addxp @user [จำนวน]` - เพิ่ม XP
- `!rank` - ดู XP ตัวเอง
- `!giverole @user [ยศ]` - แจกยศ
- `!create_private [ชื่อห้อง]` - สร้างห้องส่วนตัว
- `!announce [ข้อความ]` - ประกาศ
- `!emoji [ข้อความ]` - ตกแต่งข้อความ
- `!pinhelp` - แสดงคู่มือใช้งาน

## การตั้งค่า Bot Permissions

เมื่อเชิญบอทเข้าเซิร์ฟเวอร์ ให้เลือก permissions เหล่านี้:
- Read Messages
- Send Messages
- Connect (Voice)
- Speak (Voice)
- Manage Roles
- Manage Channels
- Pin Messages
- Manage Messages

## หมายเหตุ

- ใช้ Lavalink server ฟรี (lavalink.eu.org:2333)
- ระบบจะสร้างไฟล์ rank.json และ self_improve.log อัตโนมัติ
- สามารถปรับแต่งคำสั่งและฟีเจอร์เพิ่มเติมได้ตามต้องการ
