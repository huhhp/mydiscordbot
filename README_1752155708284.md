# Discord Music Bot (Python + wavelink)

## วิธีใช้งาน

1. สร้าง Bot ที่ [Discord Developer Portal](https://discord.com/developers/applications)
2. ตั้ง TOKEN ใน Environment Variable ชื่อ `DISCORD_TOKEN`
3. รัน `pip install -r requirements.txt`
4. รัน `python main.py` หรือ Deploy บน Render/Replit
5. เชิญบอทเข้าดิส ➜ เข้าห้องเสียง ➜ สั่งพิมพ์
   - !play [ชื่อเพลง หรือ YouTube URL]
   - !stop
   - !join / !leave
   - !ai [คุยกับบอท]
   - !addxp @user [XP]
   - !giverole @user [ชื่อยศ]
   - !create_private [ชื่อห้อง]
   - !announce [ประกาศ]
   - !emoji [ตกแต่งข้อความ]
   - !upgrade_ai
   - !pinhelp (แปะหมุดคู่มือ)

## หมายเหตุ

- ใช้ node lavalink ฟรี (lavalink.eu.org:2333)
- แก้ไขบอท/คำสั่งได้ตามต้องการ