# استخدام نسخة بايثون مستقرة وخفيفة
FROM python:3.10-slim

# تحديث مستودعات النظام وتثبيت المتطلبات الأساسية
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# تثبيت gcloud SDK (إذا كنت تحتاجه داخل الحاوية)
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg  add - && \
    apt-get update -y && apt-get install google-cloud-sdk -y

# تحديد مجلد العمل
WORKDIR /app

# نسخ ملف المتطلبات وتثبيتها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ بقية ملفات البوت
COPY . .

# أمر تشغيل البوت
CMD ["python", "bot.py"]
