FROM pytorch/pytorch:2.6.0-cuda12.4-cudnn9-runtime

WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    ffmpeg \
    curl \
    ca-certificates \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    node --version && \
    npm --version

COPY requirements.txt .
RUN python -m pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --default-timeout=1000 -r requirements.txt

COPY . .