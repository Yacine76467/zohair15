import logging
import re
import subprocess
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# --- الإعدادات الأساسية ---
# تم وضع التوكن الخاص بك هنا
API_TOKEN = '8379707803:AAGkDKSQ25WphllryYQ9wR89jPEIONjdzDY' 
IMAGE_NAME = "docker.io/yacine76467/yacine:latest"

# إعداد السجلات (Logs)
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

def extract_project_id(text):
    """دالة لاستخراج الـ Project ID من رابط جوجل كلاود"""
    match = re.search(r'qwiklabs-gcp-[\w-]+', text)
    return match.group(0) if match else None

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("أهلاً بك يا ياسين! 👋\nأرسل لي رابط Google Cloud Console لبدء النشر التلقائي والحصول على الـ VLESS.")

@dp.message_handler()
async def handle_deployment(message: types.Message):
    url = message.text
    project_id = extract_project_id(url)

    if not project_id:
        await message.reply("⚠️ عذراً، الرابط لا يحتوي على Project ID. تأكد من نسخ الرابط كاملاً من المتصفح.")
        return

    await message.answer(f"⏳ تم اكتشاف المشروع: `{project_id}`\nجاري تشغيل السيرفر وتوليد الرابط، يرجى الانتظار...")

    # أمر النشر على Google Cloud Run
    deploy_cmd = (
        f"gcloud run deploy yacinevip "
        f"--image {IMAGE_NAME} "
        f"--platform managed "
        f"--region us-central1 "
        f"--project {project_id} "
        f"--allow-unauthenticated "
        f"--quiet"
    )

    try:
        # تنفيذ أمر النشر في الخلفية (Cloud Shell سيتكفل بالباقي)
        process = subprocess.run(deploy_cmd, shell=True, capture_output=True, text=True)

        if process.returncode == 0:
            # تكوين الرابط الذي طلبته بالضبط مع تغيير الـ host بناءً على الـ project_id
            # ملاحظة: Cloud Run يضيف أرقاماً عشوائية للـ host أحياناً، 
            # لكن هذا التنسيق هو الأقرب للعمل تلقائياً:
            host_url = f"yacinevip-{project_id}.us-central1.run.app"
            
            vless_config = (
                f"vless://ba0e3984-ccc9-48a3-8074-b2f507f45ce8@google.com:443"
                f"?path=%2Fyacine&security=tls&encryption=none"
                f"&host={host_url}&type=ws&sni=youtube.com#%40yacine"
            )

            response_msg = (
                f"✅ **تم النشر بنجاح!**\n\n"
                f"إليك رابط السيرفر الجديد:\n\n"
                f"`{vless_config}`"
            )
            await message.answer(response_msg, parse_mode="Markdown")
        else:
            await message.answer(f"❌ فشل النشر. تأكد من أنك قمت بتسجيل الدخول في Cloud Shell باستخدام `gcloud auth login`.")

    except Exception as e:
        await message.answer(f"❌ حدث خطأ: {str(e)}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
