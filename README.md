# 🛡️ DARWIN — eBPF Threat Detection & Security Telemetry

DARWIN is a focused security telemetry platform that captures kernel-level process activity, streams it through a resilient pipeline, and makes suspicious behavior visible through dashboards and alerts.

This repository is built as a real-world observability prototype for:
- threat detection
- incident response validation
- security telemetry architecture
- kernel-aware monitoring

---

## What DARWIN Does

DARWIN detects suspicious process execution and privilege escalation by combining:

- **eBPF syscall tracing** for process and command execution visibility
- **Kafka event streaming** for scalable, decoupled ingestion
- **InfluxDB storage** for fast time-series analysis
- **Grafana dashboards** for monitoring and alerting
- **Telegram notifications** for critical security events

---

## Key Capabilities

- Kernel-level capture of process execution events
- Kafka-based event transport for fault tolerance and buffering
- Structured InfluxDB export for high-cardinality telemetry
- Behavior scoring and detection logic in Python
- Grafana alerting for suspicious `sudo` usage
- Documentation of detected alerts for audit readiness

---

## Architecture

1. **Sensor** — `src/sensor/` and `src/sensor/darwin_sensor.bpf.c`
   - eBPF instrumentation captures runtime process activity at the kernel boundary.
2. **Collector** — `src/collector/main.py`
   - Loads BPF and pushes raw events into Kafka topics.
3. **Bridge** — `src/bridge/exporter.py`, `src/bridge/influx_exporter.py`
   - Reads Kafka payloads and writes telemetry into InfluxDB.
4. **Intelligence** — `src/detection/`
   - Applies scoring and detection rules, then surfaces alerts.
5. **Visualization** — Grafana dashboards, alert rules, and Telegram integration.

---

## Example Alert Record
A suspicious `sudo` invocation was captured and recorded as an alert.

- Alert Name: **Suspicious Sudo Usage**
- Severity: **critical**
- Created: **2026-04-09 16:29:10**
- Summary: **Sudo command detected on Darwin-System!**

Full alert metadata:
- [SECURITY_ALERT_SUSPICIOUS_SUDO_USAGE.md](./SECURITY_ALERT_SUSPICIOUS_SUDO_USAGE.md)

---

## Visual Output

![Live System Activity](./images/Screenshot 2026-04-09 153923.png)

![Suspicious Sudo Usage Alert](./images/Screenshot 2026-04-09 163011.png)

---

## Getting Started

1. Clone the repository
   ```bash
   git clone https://github.com/harshagm665-netizen/darwin-system.git
   cd darwin-system
   ```

2. Install dependencies and prepare the environment
   ```bash
   # Follow the instructions in INSTALL.md
   ```

3. Start the platform
   ```bash
   docker compose up -d
   ```

4. Open Grafana and confirm dashboards and alerts are active.

---

## Recommended Workflow

- Extend `src/sensor/` to capture additional syscall metadata.
- Use `src/collector/` to tune Kafka serialization and topic configuration.
- Update `src/bridge/` to map new event fields into InfluxDB measurements.
- Refine detection rules in `src/detection/` for better signal quality.

---

## Notes

This repository is designed as a monitoring and detection engine, not an enforcement framework. It is ideal for security research, proof-of-concept deployments, and telemetry engineering assessments.

---

## License

MIT License. See `LICENSE` for full details.
