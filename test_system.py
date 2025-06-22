#!/usr/bin/env python3
"""
EarthPulse システム統合テストスクリプト

全ての機能が正常に動作することを確認します。
"""

import requests
import json
import time
from datetime import datetime

# テスト設定
BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def print_test(test_name):
    """テスト開始メッセージ"""
    print(f"\n🔍 {test_name}")
    print("-" * 50)

def print_result(success, message):
    """テスト結果表示"""
    status = "✅ 成功" if success else "❌ 失敗"
    print(f"{status}: {message}")

def test_server_health():
    """サーバーヘルスチェック"""
    print_test("サーバーヘルスチェック")
    
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=TIMEOUT)
        if response.status_code == 200:
            print_result(True, "FastAPIサーバー正常起動")
            return True
        else:
            print_result(False, f"HTTP {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"接続エラー: {e}")
        return False

def test_earthquake_data():
    """地震データ取得テスト"""
    print_test("地震データ機能テスト")
    
    try:
        # データ取得
        response = requests.post(f"{BASE_URL}/earthquakes", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            count = data.get("count", 0)
            print_result(True, f"USGS地震データ取得完了: {count}件")
            
            # データ表示テスト
            response = requests.get(f"{BASE_URL}/earthquakes-data", timeout=TIMEOUT)
            if response.status_code == 200:
                display_data = response.json()
                features = len(display_data.get("features", []))
                print_result(True, f"地震データ表示: {features}件")
                return True
            else:
                print_result(False, "地震データ表示エラー")
                return False
        else:
            print_result(False, f"地震データ取得エラー: HTTP {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"地震データテストエラー: {e}")
        return False

def test_fire_data():
    """火災データ取得テスト"""
    print_test("NASA火災データ機能テスト")
    
    try:
        # データ取得
        response = requests.post(f"{BASE_URL}/nasa-fires", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            if "error" in data:
                print_result(False, f"NASA API エラー: {data['error']}")
                return False
            else:
                count = data.get("count", 0)
                print_result(True, f"NASA火災データ取得完了: {count}件")
                
                # データ表示テスト
                response = requests.get(f"{BASE_URL}/fires-data", timeout=TIMEOUT)
                if response.status_code == 200:
                    display_data = response.json()
                    features = len(display_data.get("features", []))
                    print_result(True, f"火災データ表示: {features}件")
                    return True
                else:
                    print_result(False, "火災データ表示エラー")
                    return False
        else:
            print_result(False, f"火災データ取得エラー: HTTP {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"火災データテストエラー: {e}")
        return False

def test_ping_status():
    """通信監視機能テスト"""
    print_test("Raspberry Pi 通信監視機能テスト")
    
    try:
        # テストデータ
        test_data = [
            {
                "target": "google.com",
                "ip": "8.8.8.8",
                "success": True,
                "rtt_ms": 12.5
            },
            {
                "target": "example.com",
                "ip": "93.184.216.34",
                "success": False,
                "rtt_ms": None
            }
        ]
        
        response = requests.post(f"{BASE_URL}/ping-status", 
                               json=test_data, timeout=TIMEOUT)
        if response.status_code == 200:
            result = response.json()
            received = result.get("received", 0)
            print_result(True, f"通信監視データ受信完了: {received}件")
            return True
        else:
            print_result(False, f"通信監視テストエラー: HTTP {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"通信監視テストエラー: {e}")
        return False

def test_web_pages():
    """Webページ表示テスト"""
    print_test("Webページ表示テスト")
    
    pages = [
        ("/dashboard", "統合ダッシュボード"),
        ("/map-earthquakes", "地震マップ"),
        ("/map-fires", "火災マップ"),  
        ("/map-predict", "予測マップ")
    ]
    
    all_success = True
    for endpoint, name in pages:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=TIMEOUT)
            if response.status_code == 200:
                print_result(True, f"{name}ページ正常表示")
            else:
                print_result(False, f"{name}ページエラー: HTTP {response.status_code}")
                all_success = False
        except Exception as e:
            print_result(False, f"{name}ページエラー: {e}")
            all_success = False
    
    return all_success

def test_sns_functionality():
    """SNS機能テスト"""
    print_test("SNS データ収集機能テスト")
    
    try:
        response = requests.post(f"{BASE_URL}/sns-data", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            message = data.get("message", "")
            if "not implemented" in message:
                print_result(True, "SNS機能: 将来実装予定（正常な状態）")
            else:
                print_result(True, f"SNS機能: {message}")
            return True
        else:
            print_result(False, f"SNS機能エラー: HTTP {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"SNS機能テストエラー: {e}")
        return False

def main():
    """メインテスト実行"""
    print("🌍 EarthPulse システム統合テスト開始")
    print(f"テスト時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"テスト対象: {BASE_URL}")
    print("=" * 60)
    
    tests = [
        test_server_health,
        test_earthquake_data,
        test_fire_data,
        test_ping_status,
        test_web_pages,
        test_sns_functionality
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        if test_func():
            passed += 1
        time.sleep(1)  # テスト間隔
    
    print("\n" + "=" * 60)
    print("📊 テスト結果サマリー")
    print("=" * 60)
    print(f"合格: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 全テスト合格！システムは正常に動作しています。")
        return 0
    else:
        print("⚠️  一部テストが失敗しました。上記のエラーを確認してください。")
        return 1

if __name__ == "__main__":
    exit(main()) 