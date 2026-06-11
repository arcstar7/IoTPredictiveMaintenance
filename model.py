import json
import pandas as pd
import paho.mqtt.client as mqtt
import requests
from sklearn.ensemble import IsolationForest

# Configuration
BROKER_ADDRESS = "localhost"
TOPIC = "plant/floor/machine_01/telemetry"
ERP_WEBHOOK_URL = "http://your-erp-system.local/api/maintenance/trigger"

# Initialize the AI Model
# In production, you would load a pre-trained model using joblib or pickle
print("Initializing On-Premise Predictive Model...")
model = IsolationForest(contamination=0.05, random_state=42)

# Buffer to hold recent telemetry for batch predictions (if needed)
data_buffer = []

def trigger_erp_work_order(machine_id, telemetry):
    """Integrates with ERP/WMS to dispatch maintenance crews."""
    alert_payload = {
        "alert_type": "PREDICTIVE_MAINTENANCE",
        "machine_id": machine_id,
        "priority": "HIGH",
        "diagnostic_data": telemetry
    }
    try:
        # Simulate an API call to the ERP/WMS
        # response = requests.post(ERP_WEBHOOK_URL, json=alert_payload)
        print(f"\n[ALERT] Work order dispatched to ERP for {machine_id}!")
        print(f"Diagnostics: {telemetry}\n")
    except Exception as e:
        print(f"Failed to integrate with ERP: {e}")

def on_message(client, userdata, message):
    payload = json.loads(message.payload.decode("utf-8"))
    
    # Extract features for the model
    features = [[
        payload["vibration_hz"], 
        payload["temperature_c"], 
        payload["motor_rpm"]
    ]]
    
    # Note: Isolation Forest requires initial fitting. 
    # For this real-time example, we dynamically fit on a small buffer.
    # In reality, fit the model offline on historical data and strictly use .predict() here.
    data_buffer.append(features[0])
    
    if len(data_buffer) > 50:
        df = pd.DataFrame(data_buffer, columns=["vib", "temp", "rpm"])
        model.fit(df) # Update baseline
        
        # Predict on the latest incoming data point
        # Returns 1 for normal, -1 for anomaly
        prediction = model.predict(features)
        
        if prediction[0] == -1:
            trigger_erp_work_order(payload["machine_id"], payload)
            
        data_buffer.pop(0) # Keep buffer size manageable

client = mqtt.Client()
client.on_message = on_message
client.connect(BROKER_ADDRESS, 1883, 60)
client.subscribe(TOPIC)

print("AI Inference Service Listening for Telemetry...")
client.loop_forever()
