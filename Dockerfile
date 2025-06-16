# Python 3.11 slim image (マルチアーキテクチャ対応)
FROM python:3.11-slim

# 環境変数
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# システムパッケージのインストール
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    postgresql-client \
    gcc \
    libc6-dev \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリ
WORKDIR /app

# 依存関係のインストール
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードのコピー
COPY . /app/

# ポート露出
EXPOSE 8000

# 開発環境用コマンド（docker-compose で上書き）
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]