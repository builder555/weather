from location import IPLocation
from mqttpub import PublisherMQTT
from weatherapi import Weather
from time import sleep
import os

class Location:
    def __init__(self, lat, lng):
        self.latitude = lat
        self.longitude = lng

if __name__== '__main__':
    topic = os.environ.get('OUTPUT','weather')
    frequency = int(os.environ.get('UPDATE_FREQUENCY','30'))
    if loc := os.environ.get('LOCATION','').split(','):
        my_location = Location(float(loc[0]), float(loc[1]))
    else:
        my_location = IPLocation()
    weather_vars = [
        'ABOVE_TEMPERATURE',
        'BELOW_PRECIPITATION',
        'BELOW_TEMPERATURE',
        'ABOVE_PRECIPITATION'
    ]
    publish_threasholds = {
        ev.lower(): float(os.environ.get(ev)) for ev in weather_vars if os.environ.get(ev) is not None
    }
    if not publish_threasholds:
        publish_threasholds['above_temperature']=10
    mqtt = PublisherMQTT(topic)
    weather = Weather(my_location, update_frequency=frequency)
    weather.set_publisher(publisher=mqtt, **publish_threasholds)
    while True:
        sleep(0.5)
