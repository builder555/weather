from location import IPLocation
from mqttpub import PublisherMQTT
from weatherapi import Weather
from time import sleep
import os

if __name__== '__main__':
    topic = os.environ.get('output','weather')
    frequency = os.environ.get('update_frequency','30')
    weather_vars = [
        'above_temperature',
        'below_precipitation',
        'below_temperature',
        'above_precipitation'
    ]
    publish_threasholds = {
        env_var: float(os.environ.get(env_var)) for env_var in weather_vars 
                                        if os.environ.get(env_var) is not None
    }
    if not publish_threasholds:
        publish_threasholds['above_temperature']=10
    mqtt = PublisherMQTT(topic)
    weather = Weather(IPLocation(), update_frequency=frequency)
    weather.set_publisher(publisher=mqtt, **publish_threasholds)
    while True:
        sleep(0.5)
