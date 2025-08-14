from telethon import TelegramClient, events, types
import hashlib
import time
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import os
from apps.order_message import ordered_message
import hashlib

load_dotenv()

api_id=os.getenv("api_id")
api_hash=os.getenv("api_hash")
phone_number=os.getenv("phone_number")
# Telegram client
client = TelegramClient('user_session', api_id, api_hash)
seen_hashes = {}  # {hash: timestamp}
DUP_CHECK_SECONDS = 3600  # 1 soat


# Guruhlar
# source_groups = ["https://t.me/+Vy_QNJ_D8_03ZWUy"]
source_groups = ['yuk95', 'uzbekistonboylabyuklar', 'YUKMARKZIMEGA',"yukmarkazikia","isuzu_toshkent_vodiy_xizmati","sngyuklari"]
target_group = -1002805105606
target_group2 = -1002558182162

# API endpoint
api_url =os.getenv("api_url")
headers = {"Content-Type": "application/json"}



# Executor — threadlar uchun
executor = ThreadPoolExecutor(max_workers=10)


def get_message_hash(text):
    return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()

def process_message_time(msg):
    now = time.time()
    msg_hash = get_message_hash(msg)

    # Eski xabarlarni o'chirish
    for h in list(seen_hashes):
        if now - seen_hashes[h] > DUP_CHECK_SECONDS:
            del seen_hashes[h]

    # Takror tekshirish
    if msg_hash in seen_hashes:
        return None

    seen_hashes[msg_hash] = now
    return msg

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

    message = event.message
    msg_for_chek=str(message)
    if process_message_time(msg_for_chek):

        sender = await event.get_sender()
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





        # Xabarni analiz qilish (sync kod — thread pool ichida)
        try:
            results = await asyncio.get_running_loop().run_in_executor(
                executor, ordered_message, msg_text, sender.first_name, message_url, sender.id
            )
        except Exception as e:
            print("⚠️ ordered_message ishlovida xatolik:", e,msg_text)

            return

        if not results:
            return
        if not isinstance(results, list):
            results = [results]

        for result in results:
            try:
                status, response = await post_to_api(result)
                if status == 200:
                    print("✅ Yuborildi:", result.get("sellerPhoneNumber", "no-phone"))
                    print("Server:", response)
                else:
                    print(f"❌ API Xatosi [{status}]: {response}")
            except Exception as e:
                print("❌ API yuborishda xatolik:", e)
            #
            # Matnni formatlash va guruhlarga yuborish
            result_text = "\n".join(f"{k}: {v}" for k, v in result.items())
            # print(result_text)
            try:

                await asyncio.gather(

                    client.send_message(target_group, result_text),
                    client.send_message(target_group2, message.message)
                )
                print("muvafaqiyatli jonatildi")
            except Exception as e:
                print("❌ Telegramga yuborishda xatolik:", e)
    else:
        print("Takrorlangan xabar")



async def main():
    await client.start(phone_number)
    print("🚀 Bot ishga tushdi")
    await client.run_until_disconnected()


if __name__ == '__main__':
    client.loop.run_until_complete(main())
