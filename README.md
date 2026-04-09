# 🛡️ DARWIN: eBPF-Powered Intrusion Detection System

**DARWIN** (Dynamic Analysis & Real-time Watcher for Intrusion Networks) is a high-performance security telemetry pipeline. It leverages **eBPF** at the kernel level to capture system calls, streams them through **Kafka**, stores them in **InfluxDB**, and visualizes potential threats in **Grafana** with real-time **Telegram** alerting.



## 🚀 Key Features
* **Kernel-Level Visibility:** Captures `execve` syscalls using eBPF probes for zero-evasion monitoring.
* **Scalable Pipeline:** Distributed architecture using Apache Kafka to handle high-frequency event streams.
* **AI Malice Scoring:** Real-time behavioral analysis engine that flags suspicious process activity.
* **Instant Alerting:** Integrated Telegram bot for mobile notifications on privilege escalation (sudo).
* **Containerized Stack:** Full infrastructure (InfluxDB, Grafana, Kafka) deployable via Docker Compose.

## 🏗️ Architecture
The data flows through five distinct layers:
1.  **Sensor (C/eBPF):** Hooked into the Linux kernel to intercept process executions.
2.  **Collector (Python):** Loads the BPF program and publishes raw events to Kafka.
3.  **Bridge (Python):** Consumes Kafka topics and exports structured data to InfluxDB.
4.  **Intelligence (Python):** Analyzes process frequency and risk to generate a "Malice Score."
5.  **Visualization (Grafana):** Dashboarding and threshold-based alerting to Telegram.

## 🔔 Example Alert
See [SECURITY_ALERT_SUSPICIOUS_SUDO_USAGE.md](./SECURITY_ALERT_SUSPICIOUS_SUDO_USAGE.md) for a recorded Grafana alert and alert metadata.

## ⚖️ The Hard Truth (Disclaimer)
This project is an **Educational Sandbox** designed to demonstrate the eBPF telemetry stack. It is a passive observation tool and does not currently support active enforcement (blocking). It is intended for research and portfolio demonstration.

---

## 🛠️ Installation & Startup
See [INSTALL.md](./INSTALL.md) for full setup instructions.

## 📄 License
Distributed under the MIT License. See `LICENSE` for more information.
