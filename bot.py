import asyncio
import logging
import re
import subprocess
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# الإعدادات
API_TOKEN = '8379707803:AAGkDKSQ25WphllryYQ9wR89jPEIONjdzDY'
IMAGE_NAME = "docker.io/yacine76467/yacine:latest"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

def extract_project_id(text):
    match = re.search(r'qwiklabs-gcp-[\w-]+', text)
    return match.group(0) if match else None

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("أهلاً ياسين! أرسل رابط الكونسول وسأعطيك الـ VLESS.")

@dp.message()
async def handle_msg(message: types.Message):
    project_id = extract_project_id(message.text)
    if not project_id:
        await message.answer("⚠️ الرابط لا يحتوي على Project ID. انسخ الرابط من داخل الكونسول.")
        return

    msg = await message.answer(f"⏳ جاري النشر للمشروع: {project_id}...")
    
    cmd = f"gcloud run deploy yacinevip --image {IMAGE_NAME} --platform managed --region us-central1 --project {project_id} --allow-unauthenticated --quiet"
    
    process = await asyncio.create_subprocess_shell(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = await process.communicate()

    if process.returncode == 0:
        host = f"yacinevip-{project_id}.us-central1.run.app"
        vless = f"vless://ba0e3984-ccc9-48a3-8074-b2f507f45ce8@google.com:443?path=%2Fyacine&security=tls&encryption=none&host={host}&type=ws&sni=youtube.com#%40yacine"
        await msg.edit_text(f"✅ تم النشر!\n\n`{vless}`", parse_mode="Markdown")
    else:
        await msg.edit_text(f"❌ فشل: {stderr.decode()[:100]}")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
