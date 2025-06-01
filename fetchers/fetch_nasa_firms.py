# fetch_nasa_firms.py
import requests

def fetch_nasa_firms_geojson():
    """
    NASA FIRMS から24時間以内の火災データ（VIIRS）をGeoJSON形式で取得。
    出力例：https://firms.modaps.eosdis.nasa.gov/mapdata/VIIRS_Global_24h.json
    """
    url = "https://firms.modaps.eosdis.nasa.gov/mapdata/VIIRS_Global_24h.json"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {
            "type": "FeatureCollection",
            "features": [],
            "error": f"Fetch failed: {str(e)}"
        }
