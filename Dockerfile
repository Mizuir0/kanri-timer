FROM python:3.11-slim

# 環境変数設定
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 作業ディレクトリ設定
WORKDIR /app

# システムパッケージの更新とPostgreSQL client インストール
RUN apt-get update && apt-get install -y \
    postgresql-client \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Python依存関係をまずコピー
COPY requirements.txt /app/

# Python パッケージインストール
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . /app/

# ポート公開
EXPOSE 8000

# デフォルトコマンド
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]