# استخدام نسخة بايثون رسمية
FROM python:3.10-slim

# تثبيت المتطلبات الأساسية للنظام فقط
RUN apt-get update && apt-get install -y \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# تثبيت مكتبات بايثون
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# تشغيل البوت
CMD ["python", "bot.py"]
