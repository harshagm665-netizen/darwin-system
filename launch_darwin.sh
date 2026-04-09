#!/bin/bash
export PATH="$HOME/.local/bin:$PATH"
export PYTHONPATH=$(pwd)
mkdir -p logs
UV_BIN=$(which uv)

# --- CONFIGURATION ---
# Enter your Linux password here so the script can handle sudo for you
MY_PASS="cool123" 

echo "🛡️ DARWIN: Initializing Full Stack..."

# 1. Reset Infrastructure
echo $MY_PASS | sudo -S docker compose up -d

# 2. Cleanup old sessions
screen -wipe > /dev/null 2>&1

run_service() {
    local name=$1
    local cmd=$2
    echo "🚀 Starting $name..."
    screen -S "$name" -X quit > /dev/null 2>&1
    # We use 'echo password | sudo -S' to bypass the background hang
    screen -L -Logfile "logs/${name}.log" -dmS "$name" bash -c "export PYTHONPATH=$(pwd); $cmd"
}

# 3. Launch with automated sudo for the collector
run_service "darwin-collector" "echo $MY_PASS | sudo -S $UV_BIN run python -m src.collector.main"
run_service "darwin-bridge" "$UV_BIN run python -m src.bridge.influx_exporter"
run_service "darwin-detector" "$UV_BIN run python -m src.detection.detector"

echo "===================================================="
echo "✅ DARWIN ONLINE"
echo "📊 BRIDGE LOG: tail -f logs/darwin-bridge.log"
echo "📡 SENSOR LOG: tail -f logs/darwin-collector.log"
echo "===================================================="
