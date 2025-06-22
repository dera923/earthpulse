import requests

def fetch_usgs_quake_data():
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get("features", [])
    else:
        print(f"USGSデータ取得失敗: {response.status_code}")
        return []
