import sys
import time
import json
from bcc import BPF
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

# 🛡️ DARWIN Collector Configuration
KAFKA_BROKER = 'localhost:19092'
TOPIC = 'syscalls-proto'

def run_collector():
    # 1. Initialize Kafka Producer with Retry Logic
    print(f"🔄 Connecting to Redpanda at {KAFKA_BROKER}...")
    producer = None
    retries = 5
    while retries > 0:
        try:
            producer = KafkaProducer(
                bootstrap_servers=[KAFKA_BROKER],
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            break
        except NoBrokersAvailable:
            print("⏳ Waiting for Redpanda to be ready...")
            time.sleep(3)
            retries -= 1
    
    if not producer:
        print("❌ Could not connect to Kafka. Is Docker running?")
        return

    # 2. Compile and Attach eBPF Sensor
    print("🧬 Compiling eBPF Sensor...")
    try:
        b = BPF(src_file="src/sensor/darwin_sensor.bpf.c")
        b.attach_tracepoint(tp="syscalls:sys_enter_execve", fn_name="handle_execve")
    except Exception as e:
        print(f"❌ BPF Compilation Failed: {e}")
        return

    # 3. Define Callback for Kernel Events
    def send_to_kafka(cpu, data, size):
        event = b["events"].event(data)
        payload = {
            "pid": event.pid,
            "comm": event.comm.decode('utf-8', 'replace'),
            "ts": event.ts,
            "type": "EXECVE"
        }
        
        try:
            producer.send(TOPIC, payload)
            print(f"📡 Sent to Kafka: {payload['comm']} (PID: {payload['pid']})")
        except Exception as e:
            print(f"⚠️ Kafka Send Error: {e}")

    # 4. Open Buffer and Start Polling
    b["events"].open_perf_buffer(send_to_kafka)
    
    print("\n" + "="*40)
    print("🛡️  DARWIN SENSOR ACTIVE")
    print("Streaming kernel events to Redpanda...")
    print("="*40 + "\n")

    try:
        while True:
            b.perf_buffer_poll()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down DARWIN...")
        sys.exit(0)

if __name__ == "__main__":
    run_collector()
