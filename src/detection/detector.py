import json
import pandas as pd
from kafka import KafkaConsumer
from sklearn.ensemble import IsolationForest
import numpy as np

# 🛡️ DARWIN Detector Config
TOPIC = 'syscalls-proto'
KAFKA_BROKER = 'localhost:19092'

print("🧠 Initializing DARWIN AI Detector...")

# 1. Setup Kafka Consumer
consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=[KAFKA_BROKER],
    auto_offset_reset='latest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

# 2. Initialize the Isolation Forest Model
# (Contamination=0.05 means we expect ~5% of events to be "weird")
clf = IsolationForest(contamination=0.05, random_state=42)
history = []

print("📡 Listening for kernel events...")

for message in consumer:
    data = message.value
    
    # Feature Engineering: Convert 'comm' string to a numerical hash
    # In a real system, we'd use more features like frequency and user
    comm_hash = hash(data['comm']) % 1000
    pid = data['pid']
    
    current_feature = [pid, comm_hash]
    history.append(current_feature)

    # 3. Model Warm-up (Wait for 20 events to build a baseline)
    if len(history) > 20:
        # Train on the last 100 events
        train_data = np.array(history[-100:])
        clf.fit(train_data)
        
        # Predict: 1 = normal, -1 = anomaly
        score = clf.predict([current_feature])[0]
        
        status = "✅ NORMAL" if score == 1 else "⚠️  ANOMALY DETECTED"
        print(f"[{status}] PID: {pid} | COMM: {data['comm']} | Score: {score}")
    else:
        print(f"⏳ Learning baseline... ({len(history)}/20)")
