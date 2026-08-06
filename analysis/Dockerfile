FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖（包括 gcc 编译器和 ffmpeg）
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    pkg-config \
    ffmpeg \
    libavformat-dev \
    libavcodec-dev \
    libavdevice-dev \
    libavutil-dev \
    libswscale-dev \
    libswresample-dev \
    libavfilter-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "app.py"]
