import requests

def fetch_nasa_firms_geojson():
    url = "https://firms.modaps.eosdis.nasa.gov/mapserver/VIIRS_SNPP_VNP14IMG_NRT/VIIRS_SNPP_VNP14IMG_NRT.geojson"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {
            "type": "FeatureCollection",
            "features": [],
            "error": f"🔥 データ取得失敗: {str(e)}"
        }
