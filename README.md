# ThaiFlip
ตัวช่วย “พิมพ์ถูกภาษา” อัตโนมัติเมื่อเผลอพิมพ์ผิดเลย์เอาต์ EN↔TH  
เช่น `l;ylfu` → `สวัสดี`  
มี **System Tray** พร้อม **Start / Stop / Exit**, ไอคอน 🟢/🔴 แสดงสถานะ, และพาเนลเล็กชิดขอบขวาจอ

## คุณสมบัติ
- คีย์ลัด (ค่าเริ่มต้น)
  - **Alt+`** : แก้คำล่าสุด
  - **Alt+Shift+`** : แก้ข้อความที่เลือก
- Tray menu: **Start / Stop / Exit**, ไอคอนสถานะแบบซ้อนทับ (🟢 เขียว = ทำงาน, 🔴 แดง = หยุด)
- Mini panel: ปุ่ม Stop/Start, Fix selection, Always on top, Auto mode (ทดลอง)
- Allow/Deny รายชื่อโปรเซสที่ให้ทำงานได้ใน `app/settings.json`

# ThaiFlip — Logo & Branding

## Colors
- Emerald Green: #1CB941 (active / highlight)
- Stop Red: #DC2C2C (stop state)
- Midnight Slate: #1E1F26 (background)
- White: #FFFFFF

## Files
- `thaiflip-icon.svg` — App icon (rounded square) suitable to export .ico/.icns.
- `thaiflip-logo-horizontal.svg` — Horizontal lockup (glyph + wordmark).
- `thaiflip-logo-vertical.svg` — Vertical lockup.
- `thaiflip-mark.svg` — Circle mark (use as favicon).

## Export Tips
- Windows app `.ico`: export PNGs at 256/128/64/32/16 px then combine into .ico (ImageMagick or online).
- For the Tray in ThaiFlip code, you can keep using the base icon; the app will draw 🟢/🔴 overlays at runtime.


## ติดตั้ง (Windows)
1. ติดตั้ง Python 3.10+
2. โฟลเดอร์โปรเจกต์:  
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   python app\main.py
