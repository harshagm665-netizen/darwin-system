import json
import time
import sys
from kafka import KafkaConsumer
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# Config
URL = "http://localhost:8086"
TOKEN = "my-super-secret-admin-token"
ORG = "darwin_intel"
BUCKET = "syscalls"

def main():
    client = InfluxDBClient(url=URL, token=TOKEN, org=ORG)
    write_api = client.write_api(write_options=SYNCHRONOUS)
    
    consumer = KafkaConsumer(
        'syscalls-proto',
        bootstrap_servers=['localhost:19092'],
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        auto_offset_reset='earliest' # Start from the beginning of the queue
    )

    print("📡 DARWIN Bridge: Processing Kafka Queue...")

    for message in consumer:
        event = message.value
        try:
            # FORCE DATA TYPES: InfluxDB is strict!
            # If PID is a string, it will fail silently. 
            proc_name = str(event.get('comm', 'unknown'))
            pid_val = int(event.get('pid', 0))
            
            p = Point("kernel_event") \
                .tag("process", proc_name) \
                .field("pid", pid_val) \
                .time(time.time_ns(), WritePrecision.NS) # Use system time to avoid sync issues

            write_api.write(bucket=BUCKET, org=ORG, record=p)
            print(f"✅ [SUCCESS] Sent to Grafana: {proc_name}")
            
        except Exception as e:
            print(f"❌ [ERROR] Failed to write point: {e}")

if __name__ == "__main__":
    main()
