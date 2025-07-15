# Layer 4 – AWS Services

## Solution for Live Visualization

### 1) Why Live Visualization?

While storing heart rate data for later analysis is useful, there are scenarios where **real-time monitoring** is critical:

- Spotting sudden spikes or drops in heart rate.
- Providing immediate feedback during workouts.
- Triggering alerts when a predefined threshold (e.g., HR > 150 BPM) is crossed.

To address this, we built a **low-latency streaming pipeline** using managed AWS services, ending with a dynamic OpenSearch Dashboard.

---

### 2) High-Level Data Flow

```plaintext
Garmin BLE Watch 
    ↓ (via Bleak - Python)

PC (Python Script)
    ↓ (uses boto3 to send records)

Kinesis Data Stream (KDS)
    ↓ (triggers)

AWS Lambda Function (Processes & Signs Requests)
    ↓ (using SigV4-authenticated HTTP requests)

Amazon OpenSearch
    ↓ (index: heart_rate)

OpenSearch Dashboard (Line chart for real-time heart rate)

```


## 3) AWS Lambda – The Processing & Forwarding Engine

Lambda acts as the **event-driven compute layer** in this architecture.

- It gets triggered by every new record from Kinesis.
- Each record is decoded, parsed, and forwarded securely to OpenSearch.
- Supports Multiple Languages.

### 4) Why Lambda?

- Serverless and scales with traffic.
- Built-in integration with Kinesis Streams.

## 5) Important Parts of a Lambda Function Setup

Lambda functions in AWS consist of several key components that determine how they behave and integrate with other AWS services.

---

### 5.1) Code

This is the core logic of the Lambda function — written in languages like Python, Node.js, etc.

- Defines the `lambda_handler(event, context)` function.
- Processes incoming events (e.g., from Kinesis, S3, API Gateway).
- Performs actions like transformation, data forwarding, logging, etc.
- Can use environment variables for configuration.

---

### 5.2) Trigger

Triggers are AWS services that invoke the Lambda automatically.

Common examples:
- **Kinesis Data Stream** – for real-time stream processing.
   - Used in our case. A record from KDS => Code triggered to process the JSON data and post it on OS
- **S3** – to react to new file uploads.
- **API Gateway** – for serverless APIs.
- **CloudWatch Events / EventBridge** – for scheduled runs.

Trigger configuration includes:
- Event source ARN
- Batch size (for stream-based triggers)
- Filters (optional, to limit triggering conditions)

#### 5.2.1) Trigger Configuration

### 🔁 Lambda Trigger Configuration – With Meaning

| Setting       | Value                        | Meaning                                                                 |
|---------------|------------------------------|-------------------------------------------------------------------------|
| Trigger       | Kinesis Data Stream          | The Lambda is invoked **automatically** when new records arrive in KDS.|
| Batch Size    | 2 records                    | The Lambda **executes after every 2 records** are available in the stream.|
| Records/sec   | ~2 (from BLE stream)         | The BLE script sends approx. **2 heart rate records per second**.      |
| Response Time | <1 second from BLE to OS     | The **end-to-end latency** (from BLE → Lambda → OpenSearch) is typically **under 1 second**, enabling near real-time visualization. 

---

### 5.3) IAM Role (Execution Role)

Defines what resources the Lambda is **allowed to access**.

- Attached to the function via **Execution Role**.
- We should grant only least-privilege permissions.
- Common permissions include:
  - `kinesis:GetRecords`
  - `logs:CreateLogStream`, `logs:PutLogEvents`
  - `es:ESHttpPost` (for OpenSearch)
- Can also include **inline policies** or use **managed policies**.

---

### 5.4) Environment Variables

Used to inject configuration into the function **without hardcoding** it.

Examples:
- API keys
- Region names
- Domain URLs (e.g., OpenSearch endpoint)

Accessed inside code as:
```python
import os
domain = os.environ['OPENSEARCH_ENDPOINT']

---

### 5.5) Lambda Layers – Why We Needed One

1) In our case, we use the **Python runtime** in Lambda to process our JSON data from Kinesis Data Stream (KDS).  
2) However, **AWS Lambda's standard Python environment does not include external libraries** like:
   - `requests`
   - `requests_aws4auth`
3) These libraries are **essential** for making HTTP requests to OpenSearch.

### 5.5.1) Solution

- We created a **Lambda Layer** that packages the required 3rd-party dependencies.
- This layer is attached to our Lambda function, enabling it to:
  - Import those libraries at runtime.
  - Securely push records to OpenSearch.

> Without this layer, our Lambda would fail to connect to OpenSearch due to missing auth and HTTP capabilities.

---

## 🔎 Amazon OpenSearch – Real-Time Analytics Store

OpenSearch is a **distributed search and analytics engine** optimized for high-speed ingestion and querying.

It acts as our **real-time database**, receiving individual heart rate records and making them immediately searchable and visualizable.

### Why OpenSearch?

- Supports fast, filtered lookups across massive volumes.
- Natively integrates with OpenSearch Dashboard for real-time charts.
- JSON document store — ideal for time-series data like heart rate.
- Scalable, durable, and secure.

### What is OpenSearch?

- Not a traditional database.
- A **search-first document storage engine**.
- Each document is stored in JSON-like structure.
- Perfect for logging, telemetry, and live metrics dashboards.

### Configuration Summary

| Parameter            | Value                      |
|----------------------|----------------------------|
| Index Name           | `heart_rate`               |
| Timestamp Field      | `timestamp` (type: date)   |
| Heart Rate Field     | `heart_rate` (type: int)   |
| Shards               | 1                          |
| Replicas             | 1 (but yellow status due to 1-node setup) |
| Cluster Type         | Single AZ, 1-node (t3.small) |
| Storage              | EBS gp3 - 10 GiB, 3000 IOPS |
| IP Access Type       | Public IPv4                |
| Auth & Access Control| IAM + Fine-Grained via Role |

### Index Mapping

```json
{
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 1
  },
  "mappings": {
    "properties": {
      "timestamp": { "type": "date" },
      "heart_rate": { "type": "integer" }
    }
  }
}




























# Layer 4 – AWS Services  
## Solution for Live Visualization (Live-Viz)

---

## 1) Purpose

Stream and visualize real-time heart rate data from the BLE device to:

- Monitor live heart rate trends during activity
- Trigger alerts (e.g., HR > 150 bpm)
- Enable near real-time observation during tests/workouts

---

## 2) Core AWS Services Involved

| Service                   | Role in Live Visualization Pipeline                               |
|---------------------------|-------------------------------------------------------------------|
| **Amazon Kinesis Data Streams (KDS)** | Ingests real-time BLE heart rate data                 |
| **AWS Lambda**            | Processes KDS records, applies logic, and forwards to OpenSearch  |
| **Amazon OpenSearch**     | Stores live heart rate events as documents                        |
| **OpenSearch Dashboard**  | Visualizes the data via live charts and dashboards                |

---

## 3) Flow Summary

Garmin BLE (via PC) → Kinesis Data Stream → Lambda → OpenSearch → OpenSearch Dashboard

---

## 4) Key Features

- ⚡ **Near real-time** (<5s delay) data streaming and visualization  
- 🚨 **Alert triggers** handled in Lambda for high-BPM conditions  
- 📈 **Live dashboards** via OpenSearch Dashboard (no third-party UI needed)  
- 🗃️ **Time-stamped document storage** for historical drill-downs  

---

## 5) Design Trade-offs & Justifications

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


