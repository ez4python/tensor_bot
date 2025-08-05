from telethon import TelegramClient, events, types
import hashlib
import time
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import os
from apps.order_message import ordered_message

load_dotenv()

api_id=os.getenv("api_id")
api_hash=os.getenv("api_hash")
phone_number=os.getenv("phone_number")
# Telegram client
client = TelegramClient('user_session', api_id, api_hash)

# Guruhlar
# source_groups = ["https://t.me/+Vy_QNJ_D8_03ZWUy"]
source_groups = ['yuk95', 'uzbekistonboylabyuklar', 'YUKMARKZIMEGA']
target_group = -1002805105606
target_group2 = -1002558182162

# API endpoint
api_url =os.getenv("api_url")
headers = {"Content-Type": "application/json"}

# Dublikat nazorati
recent_messages = {}

# Executor — threadlar uchun
executor = ThreadPoolExecutor(max_workers=10)


async def post_to_api(data):
    async with aiohttp.ClientSession() as session:
        async with session.post(api_url, json=data, headers=headers) as resp:
            status = resp.status
            try:
                response_data = await resp.json()
            except Exception:
                response_data = await resp.text()
            return status, response_data


@client.on(events.NewMessage(chats=source_groups))
async def handler(event):
    asyncio.create_task(process_message(event))


async def process_message(event):
    sender = await event.get_sender()
    message = event.message

    chat = await event.get_chat()
    username = getattr(chat, 'username', None)

    # https://t.me/c/<chat_id_without_-100>/<message_id>

    message_url = f"https://t.me/{username}/{message.id}"

    # Bot yoki bo‘sh xabar bo‘lsa → o'tkazib yubor
    if isinstance(sender, types.User) and sender.bot:
        return
    if not message.message:
        return

    msg_text = message.message.strip()
    msg_hash = hashlib.sha256(msg_text.encode()).hexdigest()
    now = time.time()

    if msg_hash in recent_messages and now - recent_messages[msg_hash] < 60:
        return

    # Xabarni analiz qilish (sync kod — thread pool ichida)
    try:
        results = await asyncio.get_running_loop().run_in_executor(
            executor, ordered_message, msg_text, sender.first_name, message_url, sender.id
        )
    except Exception as e:
        print("⚠️ ordered_message ishlovida xatolik:", e)
        return

    if not results:
        return
    if not isinstance(results, list):
        results = [results]

    for result in results:
        # try:
        #     status, response = await post_to_api(result)
        #     if status == 200:
        #         print("✅ Yuborildi:", result.get("sellerPhoneNumber", "no-phone"))
        #         print("Server:", response)
        #     else:
        #         print(f"❌ API Xatosi [{status}]: {response}")
        # except Exception as e:
        #     print("❌ API yuborishda xatolik:", e)

        # Matnni formatlash va guruhlarga yuborish
        result_text = "\n".join(f"{k}: {v}" for k, v in result.items())
        try:
            await asyncio.gather(
                client.send_message(target_group, result_text),
                client.send_message(target_group2, message.message)
            )
        except Exception as e:
            print("❌ Telegramga yuborishda xatolik:", e)

    recent_messages[msg_hash] = now
    # Eski xabarlar tozalash
    for h, ts in list(recent_messages.items()):
        if now - ts > 60:
            del recent_messages[h]


async def main():
    await client.start(phone_number)
    print("🚀 Bot ishga tushdi")
    await client.run_until_disconnected()


if __name__ == '__main__':
    client.loop.run_until_complete(main())
