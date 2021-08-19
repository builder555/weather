from paho.mqtt import client as mqtt

class PublisherMQTT:
    def __init__(self, topic):
        self.__client = mqtt.Client()
        self.__topic = topic

    def publish(self, payload):
        self.__client.connect('mqtt', 1883)
        self.__client.publish(topic=self.__topic, payload=payload)
        self.__client.disconnect()

