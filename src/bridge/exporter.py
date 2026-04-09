import json
import time
from kafka import KafkaConsumer
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# 1. Connection Configs
token = "password123" # Use the password set in docker-compose
org = "darwin_intel"
bucket = "syscalls"
url = "http://localhost:8086"

# 2. Initialize Clients
client = InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)

consumer = KafkaConsumer(
    'syscalls-proto',
    bootstrap_servers=['localhost:19092'],
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print("🚀 DARWIN Bridge: Exporting Kafka events to InfluxDB...")

# 3. Processing Loop
try:
    for message in consumer:
        event = message.value
        
        # Create a data point for Grafana
        point = Point("syscall_event") \
            .tag("process_name", event['comm']) \
            .tag("event_type", event['type']) \
            .field("pid", event['pid']) \
            .time(time.time_ns(), WritePrecision.NS)

        write_api.write(bucket, org, point)
        print(f"📡 Exported: {event['comm']} (PID: {event['pid']})")

except KeyboardInterrupt:
    print("Stopping Bridge...")
