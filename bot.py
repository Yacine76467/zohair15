import asyncio
import logging
import re
import subprocess
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# إعدادات البوت
API_TOKEN = '8379707803:AAGkDKSQ25WphllryYQ9wR89jPEIONjdzDY'
IMAGE_NAME = "docker.io/yacine76467/yacine:latest"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

def extract_project_id(text):
    # استخراج معرف المشروع من الرابط
    match = re.search(r'qwiklabs-gcp-[\w-]+', text)
    return match.group(0) if match else None

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("✅ البوت يعمل الآن بنجاح!\nأرسل رابط Google Cloud Console وسأقوم بإنشاء السيرفر لك.")

@dp.message()
async def handle_msg(message: types.Message):
    url = message.text
    project_id = extract_project_id(url)
    
    if not project_id:
        await message.answer("⚠️ لم أتمكن من العثور على Project ID في الرابط.")
        return

    wait_msg = await message.answer(f"⏳ جاري النشر للمشروع: `{project_id}`...")
    
    # أمر النشر
    cmd = f"gcloud run deploy yacinevip --image {IMAGE_NAME} --platform managed --region us-central1 --project {project_id} --allow-unauthenticated --quiet"
    
    process = await asyncio.create_subprocess_shell(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = await process.communicate()

    if process.returncode == 0:
        host = f"yacinevip-{project_id}.us-central1.run.app"
        # تم إصلاح علامات التنصيص هنا في السطر التالي
        vless_link = f"vless://ba0e3984-ccc9-48a3-8074-b2f507f45ce8@google.com:443?path=%2Fyacine&security=tls&encryption=none&host={host}&type=ws&sni=youtube.com#%40yacine"
        await wait_msg.edit_text(f"✅ تم النشر بنجاح!\n\nرابط الـ VLESS:\n`{vless_link}`", parse_mode="Markdown")
    else:
        error_text = stderr.decode()[:150]
        await wait_msg.edit_text(f"❌ فشل النشر. تأكد من تفعيل الصلاحيات.\nالخطأ: `{error_text}`")

async def main():
    # skip_updates=True تمنع تعارض الجلسات القديمة
    await dp.start_polling(bot, skip_updates=True)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped")
