import requests

class IPLocation:
    latitude = 0
    longitude = 0
    def __init__(self):
        resp = requests.get("https://freegeoip.app/json/")
        data = resp.json()
        self.latitude = data['latitude']
        self.longitude = data['longitude']
