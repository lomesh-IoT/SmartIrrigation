import json
import base64
import os
from io import BytesIO
from django.core.management.base import BaseCommand
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from sensors.models import DHTData, PumpData, SoilMoistureData, MotionData
import paho.mqtt.client as mqtt
from sensors.utils import send_telegram_message

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPICS = {
    "dht":"sensor/dht11",
    "soil":"sensor/soil",
    "pir":  "sensor/pir",
    "pump": "sensor/pump_status"
}
 
class Command(BaseCommand):
    help = 'Starts the MQTT subscriber to listen to sensor data and save to the database.'
 
    def handle(self, *args, **options):
        def on_connect(client, userdata, flags, rc):
            print("Connected to MQTT Broker!!!!")
            for topic in MQTT_TOPICS.keys():
                client.subscribe(topic)
 
        def on_message(client, userdata, msg):
            topic = msg.topic
            data = json.loads(msg.payload.decode())
 
            if topic == "dht":
                DHTData.objects.create(temperature=data["temperature"], humidity=data["humidity"])
            elif topic == "soil":
                # Process soil moisture value to remove the '%' sign and convert to float
                soil_moisture_str = data["soil_moisture"]
                moisture_level = float(str(soil_moisture_str).replace('%', '').strip())
                SoilMoistureData.objects.create(moisture_level=moisture_level)
            elif topic == "pir":
                motion_detected=data["motion"]
                MotionData.objects.create(motion_detected=bool(data["motion"]))
                if motion_detected:
                    message = "🚨Alert... Motion detected in your farm! "
                    send_telegram_message(message)
                self.stdout.write(self.style.SUCCESS(f"Processed PIR sensor data: {data}"))
            elif topic == "pump":
                PumpData.objects.create(pumpStatus=data["pumpStatus"])
                print("Pump data saved")
            print(f"Data saved from topic {topic}: {data}")
 
        
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
 
        # Start the MQTT client loop
        client.loop_forever()
 