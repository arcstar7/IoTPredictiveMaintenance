import time
import json
import random
import paho.mqtt.client as mqtt

# Configuration for local on-premise MQTT Broker
BROKER_ADDRESS = "localhost" 
TOPIC = "plant/floor/machine_01/telemetry"

client = mqtt.Client()
client.connect(BROKER_ADDRESS, 1883, 60)

print(f"Starting IoT Sensor Simulation. Publishing to {TOPIC}...")

try:
    while True:
        # Simulating normal operational data
        sensor_data = {
            "timestamp": time.time(),
            "machine_id": "CNC_Milling_01",
            "vibration_hz": round(random.uniform(10.0, 15.0), 2),
            "temperature_c": round(random.uniform(40.0, 60.0), 2),
            "motor_rpm": round(random.uniform(1480, 1520), 0)
        }
        
        # Injecting an occasional anomaly (e.g., overheating/high vibration)
        if random.random() < 0.05: 
            sensor_data["vibration_hz"] += 25.0
            sensor_data["temperature_c"] += 30.0

        payload = json.dumps(sensor_data)
        client.publish(TOPIC, payload)
        
        print(f"Published: {payload}")
        time.sleep(2) # Transmit every 2 seconds

except KeyboardInterrupt:
    print("Simulation stopped.")
    client.disconnect()
