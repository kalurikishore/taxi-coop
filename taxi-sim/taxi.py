import asyncio
from mqtt import MQTTClient
from configuration import ConfigurationManager

from enum import Enum
from uuid import uuid4
import random
import asyncio
import datetime


class TaxiClass(int, Enum):
    DELUXE = 0
    LUXARY = 1
    UTILITY = 2

class TaxiStatus(int, Enum):
    NAVL = 0
    AVL = 1
    BOOKED = 2
    TRIP = 3

def create_random_location(south_west, north_east):
    lat = random.uniform(south_west[0], north_east[0])
    lng = random.uniform(south_west[1], north_east[1])
    return [lat, lng]

class Taxi(MQTTClient):

    def __init__(self, config: ConfigurationManager, taxi_class=TaxiClass.DELUXE):
        self._config = config
        self._taxi_id = str(uuid4())
        self._topic = self._config.topicRoot
        self._taxi_class = taxi_class
        self._status = TaxiStatus.AVL
        self._lat, self._lng = create_random_location((12.8, 77.5), (13.5, 78.2))
        self._data = dict(id=str(self._taxi_id), taxi_class=self._taxi_class, status=self._status, lat=self._lat, lng=self._lng)
        super(Taxi, self).__init__()
    
    def connect(self):
        self._connect()
    
    def disconnect(self):
        self._disconnect()
    
    def subscribe(self):
        self._subscribe(f'{self._topic}/{self._taxi_id}', callback=self._on_message)
    
    async def publish(self):
        timestamp = str(datetime.datetime.now())
        self._data['timestamp'] = timestamp
        self._publish_data(self._topic, self._data)

    def _on_message(self, client, userdata, msg):
        print(f"Message received: {msg.payload}")
    
    async def _drive(self):
        while True:
            try:
                await asyncio.sleep(random.uniform(0.2, 2.0))
                self._lat += random.uniform(-0.1, 0.1)
                self._lng += random.uniform(-0.1, 0.1)
                self._data['lat'] = self._lat
                self._data['lng'] = self._lng
            except KeyboardInterrupt:
                break

    async def main_loop(self, delay):
        while True:
            try:
                await asyncio.sleep(delay)
                await self.publish()
            except KeyboardInterrupt:
                break

        print("Closing connection ..")
        self.disconnect()
        print("Connection closed.")
    
