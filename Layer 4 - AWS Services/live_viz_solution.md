## Layer 4 – AWS Services  
### 🟢 Solution for Live Visualization (Live-Viz)

---

### 1) Purpose

Stream and visualize real-time heart rate data from the BLE device to:

- Monitor live heart rate trends during activity
- Trigger alerts (e.g., HR > 150 bpm)
- Enable near real-time observation during tests/workouts

---

### 2) Core AWS Services Involved

| Service                   | Role in Live Visualization Pipeline                               |
|---------------------------|-------------------------------------------------------------------|
| **Amazon Kinesis Data Streams (KDS)** | Ingests real-time BLE heart rate data                 |
| **AWS Lambda**            | Processes KDS records, applies logic, and forwards to OpenSearch  |
| **Amazon OpenSearch**     | Stores live heart rate events as documents                        |
| **OpenSearch Dashboard**  | Visualizes the data via live charts and dashboards                |

---

### 3) Flow Summary

Garmin BLE (via PC) → Kinesis Data Stream → Lambda → OpenSearch → OpenSearch Dashboard

---

### 4) Key Features

- ⚡ **Near real-time** (<5s delay) data streaming and visualization  
- 🚨 **Alert triggers** handled in Lambda for high-BPM conditions  
- 📈 **Live dashboards** via OpenSearch Dashboard (no third-party UI needed)  
- 🗃️ **Time-stamped document storage** for historical drill-downs  

---

### 5) Design Trade-offs & Justifications

-  **No sub-second or 1-second polling**:
  - AWS **Timestream** (best suited for time-series at that granularity) was intentionally **not used** to keep the architecture simpler and avoid service sprawl.
  - OpenSearch is capable of near real-time ingestion, but:
    -  Achieving **sub-second** streaming would require:
      - High-frequency BLE polling
      - More aggressive Lambda concurrency
      - A time-series store optimized for millisecond ingestion like Timestream or InfluxDB

-  **No Grafana integration**:
  - While OpenSearch can connect to **Grafana**, it was **intentionally avoided** to:
    - Keep the stack lean
    - Use **OpenSearch Dashboard natively**, since it supports time-series visualizations and filters out of the box

> This setup provides a balanced trade-off: **simple, low-latency, and cost-efficient** real-time visualization without introducing additional dashboarding or storage complexity.

---


