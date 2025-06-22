# 🌍 EarthPulse - 災害と通信断の相関分析システム

EarthPulseは、地震・火災などの自然災害と通信断の相関性をリアルタイムで分析・可視化するシステムです。

## 📋 システム概要

### 🎯 主要機能
- **地震データ取得**: USGSから最新の地震情報を自動取得
- **火災データ取得**: NASAから山火事・森林火災データを取得  
- **通信状況監視**: Raspberry Piネットワークによる定点通信監視
- **リアルタイム可視化**: Leaflet地図による災害・通信状況の統合表示
- **相関分析**: LLMを活用した災害と通信断パターンの分析
- **Webダッシュボード**: 統合監視ダッシュボードによる一元管理

### 🏗️ システム構成

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Perplexity    │    │   Intel NUC     │    │   Raspberry Pi  │
│      Pro        │    │   (FastAPI)     │    │   Network       │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│• 通信断原因分析 │    │• API Server     │    │• 定点Ping監視   │
│• SNS情報解析    │◄──►│• PostgreSQL DB  │◄──►│• 応答時間測定   │
│• 災害パターン   │    │• Leaflet可視化  │    │• 異常検知       │
│  学習           │    │• データ統合     │    │• HTTP POST送信  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ▲                        ▲                        ▲
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────────────────────────────────────────────────────┐
│           外部データソース (API定期取得・DB保存)                  │
├─────────────────────────────────────────────────────────────────┤
│• USGS: earthquake.usgs.gov (地震データ GeoJSON)                 │
│• NASA: firms.modaps.eosdis.nasa.gov (火災データ CSV)            │  
│• SNS: Twitter/X API (通信断報告・災害情報)                      │
│• 気象庁: NHK/Reddit等 (災害関連情報)                            │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 セットアップ手順

### 1. 前提条件
- Python 3.8+
- PostgreSQL 12+
- Git

### 2. プロジェクトクローン
```bash
git clone <repository-url>
cd earthpulse-main
```

### 3. 仮想環境セットアップ
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# または
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### 4. データベースセットアップ
```bash
# PostgreSQLにログイン
psql -U postgres

# データベース作成
CREATE DATABASE earthpulse_db;

# テーブル作成
\i create_tables.sql
```

### 5. 設定変更
```python
# app/main.py の DB接続設定を環境に合わせて変更
DB_CONFIG = {
    "user": "postgres",
    "password": "your_password",  # ← 実際のパスワードに変更
    "database": "earthpulse_db",
    "host": "localhost"
}
```

### 6. サーバー起動
```bash
# 簡単起動
./start_server.sh

# または手動起動
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 📊 アクセスURL

| 機能 | URL | 説明 |
|------|-----|------|
| 統合ダッシュボード | http://localhost:8000/dashboard | メイン監視画面 |
| 地震マップ | http://localhost:8000/map-earthquakes | 地震データ可視化 |
| 火災マップ | http://localhost:8000/map-fires | NASA火災データ表示 |
| API仕様書 | http://localhost:8000/docs | FastAPI自動生成ドキュメント |

## 🔧 API エンドポイント

### データ取得
- `POST /earthquakes` - USGSから地震データ取得・DB格納
- `POST /nasa-fires` - NASAから火災データ取得・DB格納
- `POST /sns-data` - SNSデータ収集（将来実装）

### データ提供
- `GET /earthquakes-data` - 地震データJSON取得
- `GET /fires-data` - 火災データJSON取得

### 通信監視
- `POST /ping-status` - Raspberry Piからの通信状況受信

### 分析
- `POST /infer` - 災害予測・相関分析

## 🤖 Raspberry Pi 設定

### Ping監視スクリプト例
```python
import requests
import subprocess
import json
from datetime import datetime

# 監視対象
TARGETS = [
    "google.com",
    "8.8.8.8", 
    "cloudflare.com"
]

SERVER_URL = "http://your-server:8000/ping-status"

def ping_check(target):
    try:
        result = subprocess.run(['ping', '-c', '1', target], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

# 定期実行 (cron: */5 * * * *)
def main():
    results = []
    for target in TARGETS:
        success = ping_check(target)
        results.append({
            "target": target,
            "ip": target,
            "success": success,
            "rtt_ms": 0.0 if not success else 10.0
        })
    
    requests.post(SERVER_URL, json=results)

if __name__ == "__main__":
    main()
```

## 📈 データベーススキーマ

### テーブル構成
- `earthquake_data`: 地震情報
- `fire_data`: 火災情報
- `network_check`: 通信監視結果
- `communication_reports`: SNS/通信断報告

## 🔍 トラブルシューティング

### よくある問題

1. **データベース接続エラー**
   ```
   解決法: PostgreSQLが起動していることを確認
   sudo systemctl start postgresql
   ```

2. **ポート8000が使用中**
   ```
   解決法: 別のポートを使用
   uvicorn app.main:app --port 8001
   ```

3. **NASA APIタイムアウト**
   ```
   解決法: ネットワーク接続とFirewall設定を確認
   ```

## 🎯 今後の拡張予定

- [ ] Twitter API v2 統合によるSNSデータ収集
- [ ] 機械学習による災害予測精度向上
- [ ] Slack/LINE通知機能
- [ ] モバイルアプリ対応  
- [ ] 多言語対応（英語・中国語）

## 📝 ライセンス

MIT License

## 👥 貢献

プルリクエストやイシューの報告を歓迎します。

---

**🚨 重要な注意事項**
- 本システムは研究・学習目的で開発されています
- 実際の災害対応には公式機関の情報を優先してください  
- Twitter API利用には申請・審査が必要です
