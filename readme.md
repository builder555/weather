### Balena Blocks: binary weather

Uses an [API](https://api.met.no/weatherapi) to get weather, and publish a message to MQTT based on set conditions. Uses public IP to get location.

___Usage a block___

Add the following to your `docker-compose.yaml`:

```yaml
  weather:
    build: ./weather
    restart: always
    environment: 
      - OUTPUT=weather_1
      - ABOVE_TEMPERATURE=10
      - BELOW_PRECIPITATION=15
```

___Available variables___

- `OUTPUT`: MQTT topic to publish the results to
- `UPDATE_FREQUENCY`: how often (in minutes) to fetch the weather forecast
- `ABOVE_TEMPERATURE`: will publish '1' when current temperature (in C) is above this temperature, '0' otherwise
- `BELOW_TEMPERATURE`: will publish '1' when current temperature is below this temperature, '0' otherwise
- `ABOVE_PRECIPITATION`: will publish '1' when forecast (for next 12 hours) calls for precipitation amount (in mm) that is above this value, '0' otherwise
- `BELOW_PRECIPITATION`: will publish '1' when forecast (for next 12 hours) calls for precipitation amount that is below this value, '0' otherwise
- `LOCATION`: location to use for weather, specified in latitude,longitude format. If not specified, geolocation of the public IP address will be used

All the temperature/precipitation arguments are ANDed together, i.e. if both (above/below) temperature arguments are set, it will only publish '1' when the temperature(T) is `ABOVE_TEMPERATURE` < T < `BELOW_TEMPERATURE`. if all four are set, then it will only publish '1' if temperature is `ABOVE_TEMPERATURE` < T < `BELOW_TEMPERATURE` AND precipitation (P) is `ABOVE_PRECIPITATION` < P < `BELOW_PRECIPITATION`.

___Environment variables defaults___

- `OUTPUT`: "weather"
- `UPDATE_FREQUENCY`: 30
- `ABOVE_TEMPERATURE`: 10 
> ___N.B.___: `ABOVE_TEMPERATURE` is set to 10 by default _only_ if no other temperature/precipitation parameter is set.

___Tests___

```bash
$ PIPENV_VENV_IN_PROJECT=1 pipenv install --dev
$ pipenv shell
$ pytest -vs
```

___Standalone usage___

Publish MQTT message '1' when specified temperature/precipitation is reached.

Given the code
```python
>>> from location import IPLocation
>>> from mqttpub import PublisherMQTT
>>> from weatherapi import Weather
>>> from time import sleep
>>> import os
>>> 
>>> mqtt = PublisherMQTT('weather')
>>> weather = Weather(IPLocation(), update_frequency=30)
>>> weather.set_publisher(publisher=mqtt, above_temperature=15)
>>> while True:
>>>     sleep(0.5)
```
A message will be published every 30 minutes with payload '1' under topic 'weather' if the temperature at that time is above 15C or '0' if it's 15C or lower.

> N.B. mqtt connects to host 'mqtt' on port 1883
_logo image by [yusup saputra](https://thenounproject.com/dysastudio)_
