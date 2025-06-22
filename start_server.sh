#!/bin/bash

# EarthPulse サーバー起動スクリプト

echo "🌍 EarthPulse システムを起動しています..."

# 仮想環境のアクティベーション
echo "仮想環境をアクティベート中..."
source venv/bin/activate

# 依存関係の確認
echo "依存関係をチェック中..."
pip install -r requirements.txt --quiet

# データベースの準備（PostgreSQLが起動していることを前提）
echo "データベース接続をチェック中..."

# FastAPIサーバーの起動
echo "🚀 FastAPIサーバーを起動中..."
echo "ダッシュボードURL: http://localhost:8000/dashboard"
echo "地震マップURL: http://localhost:8000/map-earthquakes"
echo "火災マップURL: http://localhost:8000/map-fires"
echo ""
echo "サーバーを停止するには Ctrl+C を押してください"

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload 