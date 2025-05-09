import json
import paho.mqtt.client as mqtt
from django.core.management.base import BaseCommand
from sensors.models import DHTData, PumpData, SoilMoistureData, MotionData

# MQTT configuration
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPICS = {
    "sensor/dht11": "dht",
    "sensor/soil": "soil",
    "sensor/pir": "pir",
    "sensor/pump_status": "pump"
}

class Command(BaseCommand):
    help = 'Starts the MQTT subscriber to listen to sensor data and save to the database.'

    def handle(self, *args, **options):
        def on_connect(client, userdata, flags, rc):
            print("Connected to MQTT Broker!")
            for topic in MQTT_TOPICS.keys():
                client.subscribe(topic)

        def on_message(client, userdata, msg):
            topic = msg.topic
            data = json.loads(msg.payload.decode())

            if topic == "sensor/dht11":
                DHTData.objects.create(temperature=data["temperature"], humidity=data["humidity"])
            elif topic == "sensor/soil":
                # Process soil moisture value to remove the '%' sign and convert to float
                soil_moisture_str = data["soil_moisture"]
                moisture_level = float(soil_moisture_str.replace('%', '').strip())
                SoilMoistureData.objects.create(moisture_level=moisture_level)
            elif topic == "sensor/pir":
                MotionData.objects.create(motion_detected=bool(data["motion"]))
            elif topic == "sensor/pump_status":
                PumpData.objects.create(pumpStatus=data["pumpStatus"])
                print("Pump data saved")

            print(f"Data saved from topic {topic}: {data}")

        # Initialize the MQTT client
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(MQTT_BROKER, MQTT_PORT, 60)

        # Start the MQTT client loop
        client.loop_forever()