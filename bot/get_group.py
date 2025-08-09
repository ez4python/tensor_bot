from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError, AuthRestartError
import os

api_id = os.getenv("api_id")
api_hash = os.getenv("api_hash")
phone_number = os.getenv("phone_number")

client = TelegramClient('user_session', api_id, api_hash)

try:
    client.connect()

    if not client.is_user_authorized():
        print("📲 Kod so‘ralmoqda...")
        client.send_code_request(phone_number)
        code = input("✅ Telegramdan kelgan 5 xonali kodni kiriting: ")
        try:
            client.sign_in(phone_number, code)
        except SessionPasswordNeededError:
            password = input("🔐 2-bosqichli parolingizni kiriting: ")
            client.sign_in(password=password)

    # Agar login muvaffaqiyatli bo‘lsa, dialoglar ro‘yxatini chiqaramiz
    dialogs = client.get_dialogs()
    if dialogs:
        print("\n✅ Sizda mavjud dialoglar:")
        for dialog in dialogs:
            print(f"{dialog.name} — {dialog.id}")
    else:
        print("❗️ Chatlar topilmadi. Balki sizda hech qanday chat ochilmagan bo‘lishi mumkin.")

except AuthRestartError:
    print("❌ Telegram AuthRestartError xatosi: Iltimos, 1 daqiqa kuting va qaytadan urinib ko‘ring.")
except Exception as e:
    print(f"❌ Noma’lum xatolik yuz berdi: {e}")

finally:
    client.disconnect()
