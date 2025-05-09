#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>

// Replace with your network credentials
const char* ssid = "RedmiPower";
const char* password = "Prerana123";

// MQTT Broker details
const char* mqtt_server = "broker.emqx.io";

// Define MQTT topics
const char* tempHumTopic = "sensor/dht11";
const char* soilMoistureTopic = "sensor/soil";
const char* pirTopic = "sensor/pir";
const char* pumpStatusTopic = "sensor/pump_status";  // Topic for pump status


// Define DHT11 sensor parameters
#define DHTPIN 4  // DHT11 connected to GPIO4
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// Define other sensor pins
#define SOIL_MOISTURE_PIN 33  // Soil moisture analog pin
#define PIR_PIN 14            // PIR sensor connected to GPIO14
#define PUMP_PIN 12           // Relay connected to GPIO12 to control the pump

WiFiClient espClient;
PubSubClient client(espClient);
unsigned long lastMsg = 0;
const long interval = 2000;  // Publish interval in milliseconds

// Calibration values for soil moisture
int raw_min = 0;         // Update this with the reading from fully saturated soil
int raw_max = 4095;      // Update this with the reading from completely dry soil

// Thresholds for controlling the pump (adjust these as needed)
const float soilMoistureThresholdLow = 50.0;  // Moisture below this value will turn the pump on
const float soilMoistureThresholdHigh = 70.0; // Moisture above this value will turn the pump off

// Function to connect to WiFi
void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

// Function to connect to the MQTT broker
void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("ESP32Client")) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

// Function to control the pump
void controlPump(bool turnOn) {
  if (turnOn) {
    digitalWrite(PUMP_PIN, HIGH);  // Turn pump ON
    // Publish pump status as JSON payload
    String pumpStatusPayload = "{\"pumpStatus\": \"" + String(turnOn ? "ON" : "OFF") + "\"}";
    client.publish(pumpStatusTopic, pumpStatusPayload.c_str());
    Serial.println("Pump ON");
  } else {
    digitalWrite(PUMP_PIN, LOW);   // Turn pump OFF
    // Publish pump status as JSON payload
    String pumpStatusPayload = "{\"pumpStatus\": \"OFF\"}";
    client.publish(pumpStatusTopic, pumpStatusPayload.c_str());
    Serial.println("Pump OFF");
  }
}

void setup() {
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  dht.begin();

  pinMode(SOIL_MOISTURE_PIN, INPUT);
  pinMode(PIR_PIN, INPUT);
  pinMode(PUMP_PIN, OUTPUT);  // Set the pump control pin as output

  digitalWrite(PUMP_PIN, LOW);  // Ensure the pump is off initially
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  unsigned long now = millis();
  if (now - lastMsg > interval) {
    lastMsg = now;

    // Read DHT11 data
    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();

    if (!isnan(temperature) && !isnan(humidity)) {
      String tempHumPayload = "{\"temperature\": " + String(temperature) + ", \"humidity\": " + String(humidity) + "}";
      client.publish(tempHumTopic, tempHumPayload.c_str());
      Serial.println("DHT11 Data Published: " + tempHumPayload);
    } else {
      Serial.println("Failed to read from DHT sensor!");
    }

    // Read and convert Soil Moisture data using new calibration
    int raw_value = analogRead(SOIL_MOISTURE_PIN);
    Serial.print("Raw Soil Moisture Value: ");
    Serial.println(raw_value);

    // Calculate soil moisture percentage
    float soilMoisturePercentage = 100.0 * (raw_max - raw_value) / (raw_max - raw_min);
    soilMoisturePercentage = constrain(soilMoisturePercentage, 0, 100);  // Constrain to 0-100%

    // Prepare soil moisture payload and publish it
    String soilMoisturePayload = "{\"soil_moisture\": \"" + String(soilMoisturePercentage) + "%\"}";
    client.publish(soilMoistureTopic, soilMoisturePayload.c_str());
    Serial.println("Soil Moisture Data Published: " + soilMoisturePayload);

    // Control the pump based on soil moisture
    if (soilMoisturePercentage < soilMoistureThresholdLow) {
      controlPump(true);  // Turn pump ON if soil moisture is below the low threshold
    } else if (soilMoisturePercentage > soilMoistureThresholdHigh) {
      controlPump(false); // Turn pump OFF if soil moisture is above the high threshold
    }

    // Read PIR data
    int pirState = digitalRead(PIR_PIN);
    String pirPayload = "{\"motion\": " + String(pirState) + "}";
    client.publish(pirTopic, pirPayload.c_str());
    Serial.println("PIR Data Published: " + pirPayload);
  }
}
