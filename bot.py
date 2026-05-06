import os
import re
import logging
import subprocess
from aiogram import Bot, Dispatcher, types, executor

# الإعدادات - استبدل كلمة yacine فقط بتوكن البوت الخاص بك
API_TOKEN = "8379707803:AAGkDKSQ25WphllryYQ9wR89jPEIONjdzDY" 

MY_IMAGE = "docker.io/yacine76467/yacine:latest"
MY_UUID = "ba0e3984-ccc9-48a3-8074-b2f507f45ce8"
MY_PATH = "/yacine"
MY_SNI = "googleusercontent.com"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("👋 أهلاً بك! أرسل رابط Google Cloud Console لبدء النشر التلقائي.")

@dp.message_handler()
async def deploy_handler(message: types.Message):
    text = message.text
    # استخراج الـ Project ID من الرابط المرسل
    match = re.search(r'project=([^&?#\s]+)', text)
    
    if match:
        project_id = match.group(1)
        await message.answer(f"⏳ جاري العمل على المشروع: `{project_id}`...", parse_mode='Markdown')
        
        try:
            # تعيين المشروع النشط في gcloud
            subprocess.run(f"gcloud config set project {project_id} --quiet", shell=True)
            
            # أمر نشر الحاوية على Cloud Run
            deploy_cmd = (
                f"gcloud run deploy vless-service "
                f"--image={MY_IMAGE} "
                f"--platform=managed "
                f"--region=us-central1 "
                f"--allow-unauthenticated "
                f"--port=8080 "
                f"--format='value(status.url)'"
            )
            
            process = subprocess.Popen(deploy_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            output = stdout.decode().strip()

            if output and "run.app" in output:
                clean_url = output.replace("https://", "")
                # بناء رابط الـ VLESS النهائي
                vless_link = f"vless://{MY_UUID}@{clean_url}:443?path={MY_PATH}&security=tls&encryption=none&host={clean_url}&type=ws&sni={MY_SNI}#@yacine_GCloud"
                await message.answer(f"✅ تم الإنشاء بنجاح!\n\n`{vless_link}`", parse_mode='Markdown')
            else:
                error_msg = stderr.decode()
                await message.answer(f"❌ فشل النشر. تأكد من تفعيل الـ Cloud Run API وصلاحيات الحساب.\n\n`{error_msg[:150]}`", parse_mode='Markdown')
        except Exception as e:
            await message.answer(f"حدث خطأ داخلي: {str(e)}")
    else:
        await message.answer("⚠️ عذراً، الرابط لا يحتوي على Project ID. تأكد من نسخ الرابط كاملاً.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
