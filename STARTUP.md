# 🛡️ DARWIN Startup Guide
**Dynamic Analysis & Real-time Watcher for Intrusion Networks**

> eBPF-powered security telemetry pipeline: kernel syscall capture → Kafka → InfluxDB → Grafana + Telegram alerting.

---

## Prerequisites

| Requirement | Minimum Version | Notes |
|---|---|---|
| Linux Kernel | 5.8+ | Required for eBPF CO-RE support |
| Docker Engine | 24.x+ | Native install, not Docker Desktop |
| Python | 3.10+ | Managed via `uv` |
| RAM | 4 GB+ | Kafka + InfluxDB + Grafana are memory-heavy |
| Privileges | `sudo` access | eBPF sensor requires root |

> ⚠️ **WSL2 Users:** eBPF works on WSL2 only with kernel 5.15+ (Ubuntu 22.04 default). Run `uname -r` to verify. The eBPF sensor may require `--privileged` mode in WSL2.

---

## Phase 1: Environment Setup

### Step 1 — Verify Kernel Version

```bash
uname -r
# Expected output: 5.8.x or higher (e.g., 6.8.0-51-generic)
```

If your kernel is below 5.8, upgrade before proceeding:

```bash
sudo apt update && sudo apt full-upgrade -y
sudo reboot
```

---

### Step 2 — Install Core Dependencies

```bash
# Update package index and install essentials
sudo apt update && sudo apt install -y \
  git \
  curl \
  build-essential \
  linux-headers-$(uname -r)
```

> 📝 `linux-headers` are required by BCC/eBPF tools to compile kernel probes at runtime.

---

### Step 3 — Install Docker Engine

```bash
# Download and run the official Docker install script
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to the docker group (avoids needing sudo for docker commands)
sudo usermod -aG docker $USER

# Apply group change without logging out
newgrp docker

# Verify installation
docker --version
docker compose version
```

> ⚠️ **Important:** The `newgrp docker` command applies the group change in the current shell session only. For a permanent effect across all terminals, log out and log back in, or run `su - $USER`.

---

### Step 4 — Install Python via `uv`

`uv` is a Rust-based Python package manager — significantly faster than `pip` or `poetry`.

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Load uv into the current shell (add this to ~/.bashrc or ~/.zshrc for persistence)
source $HOME/.local/bin/env

# Verify
uv --version
```

> 📝 The original install docs referenced `$HOME/.cargo/env`, which is the Rust toolchain path. The correct `uv` env path is `$HOME/.local/bin/env`. If `uv` is not found after install, run:
> ```bash
> export PATH="$HOME/.local/bin:$PATH"
> ```

---

## Phase 2: Project Initialization

### Step 1 — Clone the Repository

```bash
git clone https://github.com/harshagm665-netizen/darwin-system.git
cd darwin-system
```

---

### Step 2 — Install Python Dependencies

```bash
# Install all project dependencies defined in pyproject.toml
uv sync
```

---

### Step 3 — Configure Secrets (`.env`)

Create the `.env` file in the project root:

```bash
cp .env.example .env   # Use this if an example file exists
# OR
nano .env              # Create from scratch
```

Paste and fill in the following:

```env
# Telegram Bot (get from @BotFather on Telegram)
TELEGRAM_TOKEN=your_bot_token_from_botfather

# Your Telegram Chat ID (get from @userinfobot on Telegram)
TELEGRAM_CHAT_ID=your_numeric_chat_id

# InfluxDB Admin Token (must match the value in docker-compose.yml)
INFLUXDB_TOKEN=my-super-secret-admin-token
INFLUXDB_ORG=darwin-org
INFLUXDB_BUCKET=syscalls
INFLUXDB_URL=http://localhost:8086

# Kafka Broker Address
KAFKA_BROKER=localhost:9092
KAFKA_TOPIC=syscall-events
```

> 🔐 **Never commit `.env` to Git.** Verify it is listed in `.gitignore`:
> ```bash
> grep ".env" .gitignore
> ```

---

## Phase 3: Launch the Stack

### Step 1 — Start Infrastructure (Docker)

This spins up Kafka, Zookeeper, InfluxDB, and Grafana as background containers.

```bash
# Start all services defined in docker-compose.yml
docker compose up -d

# Verify all containers are running (should show 4+ healthy containers)
docker compose ps
```

**Expected running services:**

| Container | Port | Purpose |
|---|---|---|
| `zookeeper` | 2181 | Kafka dependency |
| `kafka` | 9092 | Event stream broker |
| `influxdb` | 8086 | Time-series storage |
| `grafana` | 3000 | Dashboard & alerting |

> ⚠️ **Wait ~15–20 seconds** after `up -d` before starting telemetry services. Kafka requires Zookeeper to be healthy first. To wait explicitly:
> ```bash
> docker compose up -d && sleep 20
> ```

---

### Step 2 — Start Telemetry Services

#### Option A: Master Launch Script (Recommended)

```bash
chmod +x launch_darwin.sh
./launch_darwin.sh
```

#### Option B: Manual Execution (for debugging)

Open **three separate terminal windows** and run one command per terminal:

```bash
# Terminal 1 — Bridge: reads from Kafka, writes to InfluxDB
uv run python -m src.bridge.influx_exporter
```

```bash
# Terminal 2 — Detection Engine: anomaly scoring and Telegram alerts
uv run python -m src.detection.detector
```

```bash
# Terminal 3 — eBPF Kernel Sensor (MUST run as root)
sudo uv run python -m src.collector.collector
```

> ⚠️ The collector **must** run as root (`sudo`) because eBPF requires `CAP_SYS_ADMIN` or root privileges to attach kernel probes. Running without `sudo` will raise a `PermissionError`.

---

## Phase 4: Visualization & Alerting

### Step 1 — Access Grafana Dashboard

1. Open your browser: [http://localhost:3000](http://localhost:3000)
2. Log in with default credentials: **Username:** `admin` / **Password:** `admin`
3. You will be prompted to change the password on first login.
4. Import the dashboard:
   - Go to **Dashboards → Import**
   - Click **Upload JSON file**
   - Select: `grafana/provisioning/dashboards/darwin_main.json`
   - Click **Import**

---

### Step 2 — Configure InfluxDB Data Source (First-time only)

If Grafana does not auto-detect InfluxDB:

1. Go to **Connections → Data Sources → Add data source**
2. Select **InfluxDB**
3. Set:
   - **URL:** `http://influxdb:8086` *(use container name, not localhost, inside Docker network)*
   - **Auth token:** value of `INFLUXDB_TOKEN` from your `.env`
   - **Organization:** `darwin-org`
   - **Default Bucket:** `syscalls`
4. Click **Save & Test** — should show ✅ green

---

### Step 3 — Trigger a Test Alert

In a new terminal, simulate privileged access (a monitored syscall pattern):

```bash
sudo ls /root
sudo cat /etc/shadow 2>/dev/null || true
```

**Expected results within ~15 seconds:**
- 📊 A spike appears in the **"Live System Activity"** Grafana panel
- 📱 A Telegram notification is delivered to your configured chat

---

## Troubleshooting

### Docker containers not starting

```bash
# View logs for a specific service
docker compose logs kafka
docker compose logs influxdb

# Restart a specific service
docker compose restart kafka
```

### eBPF sensor permission error

```bash
# Confirm you are running with sudo
sudo uv run python -m src.collector.collector

# Check if BCC tools are installed (needed for kernel probe compilation)
python3 -c "import bcc; print(bcc.__version__)"
```

### Kafka connection refused

```bash
# Confirm Kafka is listening on port 9092
nc -zv localhost 9092

# If not, check Zookeeper is healthy first
docker compose logs zookeeper
```

### `uv` command not found

```bash
export PATH="$HOME/.local/bin:$PATH"
source $HOME/.local/bin/env
```

---

## Stopping DARWIN

```bash
# Stop all telemetry services
# (Use Ctrl+C in each terminal running uv services)

# Stop and remove Docker containers
docker compose down

# Stop and remove containers + delete all data volumes (full reset)
docker compose down -v
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                   Linux Kernel                       │
│  eBPF Hook → intercepts execve/open/connect syscalls │
└───────────────────────┬─────────────────────────────┘
                        │ raw syscall events
                        ▼
              ┌─────────────────┐
              │  collector.py   │  (runs as root)
              └────────┬────────┘
                       │ JSON events
                       ▼
              ┌─────────────────┐
              │  Kafka Broker   │  topic: syscall-events
              └────┬────────────┘
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
┌──────────────┐     ┌────────────────┐
│influx_exporter│     │   detector.py  │
│ (bridge)      │     │ anomaly scorer │
└──────┬───────┘     └───────┬────────┘
       │ writes                │ fires alert
       ▼                       ▼
┌──────────────┐     ┌────────────────┐
│   InfluxDB   │     │    Telegram    │
│ (time-series)│     │  notification  │
└──────┬───────┘     └────────────────┘
       │ queries
       ▼
┌──────────────┐
│    Grafana   │  → http://localhost:3000
│  (dashboard) │
└──────────────┘
```

---

## Disclaimer

DARWIN is an **educational security sandbox** for learning eBPF, Kafka, and big-data telemetry pipelines. It is a **passive monitoring tool** — it observes and records syscall activity but does **not** block or modify system calls. It is intended for research, portfolio demonstration, and learning the Linux observability stack on controlled/owned systems only.

---

*Licensed under the MIT License.*
