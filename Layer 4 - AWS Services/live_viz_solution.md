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
---

## A) AWS Lambda – The Processing & Forwarding Engine

Lambda acts as the **event-driven compute layer** in this architecture.

- It gets triggered by every new record from Kinesis.
- Each record is decoded, parsed, and forwarded securely to OpenSearch.
- Supports Multiple Languages.

### 1) Why Lambda?

- Serverless and scales with traffic.
- Built-in integration with Kinesis Streams.

## 2) Important Parts of a Lambda Function Setup

Lambda functions in AWS consist of several key components that determine how they behave and integrate with other AWS services.

---

### 3.1) Code

This is the core logic of the Lambda function — written in languages like Python, Node.js, etc.

- Defines the `lambda_handler(event, context)` function.
- Processes incoming events (e.g., from Kinesis, S3, API Gateway).
- Performs actions like transformation, data forwarding, logging, etc.
- Can use environment variables for configuration.

[Run post configuring IAM Roles, OpenSearch Domain. Seen in Repo as lambda_os.py](https://github.com/adiman1/liveheartrate/blob/0fce4fbb24fb32ec6e4438bb98cceb8b12516eea/Layer%204%20-%20AWS%20Services/lambda_os.py)

---

### 3.2) Trigger

Triggers are AWS services that invoke the Lambda automatically.

Common examples:
- **Kinesis Data Stream** – for real-time stream processing.
   - Used in our case. A record from KDS => Code triggered to process the JSON data and post it on OS
- **S3** – to react to new file uploads.
- **API Gateway** – for serverless APIs.
- **CloudWatch Events / EventBridge** – for scheduled runs.
---

### 3.2.1) Trigger Configuration

### Lambda Trigger Configuration – With Meaning

| Setting       | Value                        | Meaning                                                                 |
|---------------|------------------------------|-------------------------------------------------------------------------|
| Trigger       | Kinesis Data Stream          | The Lambda is invoked **automatically** when new records arrive in KDS.|
| Batch Size    | 2 records                    | The Lambda **executes after every 2 records** are available in the stream.|
| Records/sec   | ~2 (from BLE stream)         | The BLE script sends approx. **2 heart rate records per second**.      |
| Response Time | <1 second from BLE to OS     | The **end-to-end latency** (from BLE → Lambda → OpenSearch) is typically **under 1 second**, enabling near real-time visualization. 

![KDS Trigger](https://github.com/adiman1/liveheartrate/blob/982020d39fd79884fb12f874d58aabf8be9e8d9e/Layer%204%20-%20AWS%20Services/images/Lambda%20Structure.png)

---

### 3.3) IAM Role (Execution Role)

Defines what resources the Lambda is **allowed to access**.

- Attached to the function via **Execution Role**.
- We should grant only least-privilege permissions.
- Common permissions include:
  - `kinesis:GetRecords` (to fetch KDS records)
  - `logs:CreateLogStream`, `logs:PutLogEvents`
  - `es:ESHttpPost` (for post in OpenSearch)
- Can also include **inline policies** or use **managed policies**.

---

### 3.4) Environment Variables

Used to inject configuration into the function **without hardcoding** it.

Examples:
- API keys
- Region names
- Domain URLs (e.g., OpenSearch endpoint)

Accessed inside code as:

```python
import os
domain = os.environ['OPENSEARCH_ENDPOINT']
```
---

### 3.5) Lambda Layers – Why We Needed One

1) In our case, we use the **Python runtime** in Lambda to process our JSON data from Kinesis Data Stream (KDS).  
2) However, **AWS Lambda's standard Python environment does not include external libraries** like:
   - `requests`
   - `requests_aws4auth`
3) These libraries are **essential** for making HTTP requests to OpenSearch.

### 3.5.1) Solution

- We created a **Lambda Layer** that packages the required 3rd-party dependencies.
- This layer is attached to our Lambda function, enabling it to:
  - Import those libraries at runtime.
  - Securely push records to OpenSearch.

> Without this layer, our Lambda would fail to connect to OpenSearch due to missing Auth and HTTP capabilities.

---

## B) Amazon OpenSearch – Real-Time Analytics Store

OpenSearch is a **distributed search and analytics engine** optimized for high-speed ingestion and querying.

It acts as our **real-time database**, receiving individual heart rate records and making them immediately searchable and visualizable.

---

### 1) What is OpenSearch?

- Not a traditional database.
- A **search-first document storage engine**.
- Each document is stored in JSON-like structure.
- Supports fast, filtered lookups across massive volumes.
- Natively integrates with OpenSearch Dashboard for real-time charts.
- Perfect for logging, telemetry, and live metrics dashboards.

---

### 2) OpenSearch Structure Overview

OpenSearch stores and organizes data in a **hierarchical structure** similar to a database system but optimized for search and analytics.

---

### 3) Core Concepts

| Concept        | Description                                                                 |
|----------------|-----------------------------------------------------------------------------|
| **Cluster**    | A group of one or more nodes (servers) that holds all data and handles requests. |
| **Node**       | A single instance of OpenSearch. In our case, we used a single-node cluster. |
| **Index**      | Equivalent to a **table** in a database. Each index stores a set of documents. |
| **Document**   | A **JSON object** representing a single record (e.g., one heart rate reading). |
| **Mapping**    | The **schema definition** of an index. It defines the fields, types, and structure. |
| **Shard**      | A physical division of an index. Enables horizontal scalability and parallelism. |
| **Replica**    | A copy of a shard for fault tolerance. Stored on a different node than the primary shard. |

---

### 3.1) Index Mapping: `heart_rate`

In our setup, we created an index called **`heart_rate`**, which stores real-time HR data streamed from BLE to OpenSearch via Lambda.

Here’s the mapping configuration used:

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
```

---

### 3.1.1) What Are Indexes Used For?

Indexes in OpenSearch are like **optimized databases for search and analytics**. They are used to:

- **Store structured JSON documents** (e.g., heart rate, timestamp).
- **Enable fast full-text and field-based search** using inverted indexes.
- **Perform time-based filtering and aggregation**, making them perfect for time-series data like heart rate streams.
- **Enable analytics**, dashboards, and alerting using built-in tools or external platforms like Grafana.

In our project:

- The **`heart_rate` index** stores each record coming from the BLE → Kinesis → Lambda → OpenSearch pipeline.
- Each record is a document with structure:
  ```json
  {
    "timestamp": "2025-07-15T17:10:33",
    "heart_rate": 89
  }

This enables us to slice, query, and visualize heart rate trends over time.

---

### 4) Configuration Summary

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

## C) OpenSearch Dashboards – Real-Time Visualization

1) OpenSearch Dashboards is the **visual interface** for exploring and interacting with data stored in OpenSearch indexes. 
2) It helps in building live charts, analyzing trends, and setting up observability for time-series data.

---

### 6) Purpose in Our Architecture

- To **monitor heart rate data in near real-time**.
- To visually validate that data streamed from the BLE device → PC → Kinesis → Lambda → OpenSearch is being captured and indexed correctly.
- To identify spikes or abnormalities (e.g., heart rate > 150 bpm) quickly.

---

### 7) Dashboard Configuration

| Setting             | Value                                  |
|---------------------|----------------------------------------|
| **Chart Type**      | Line Chart                             |
| **X-Axis**          | `timestamp` (aggregated per 5 seconds) |
| **Y-Axis**          | `heart_rate` (Last value)              |
| **Metric Used**     | Last heart rate per 5-sec window       |
| **Index Pattern**   | `heart_rate`                           |
| **Update Frequency**| Near real-time (~1 second delay)       |
| **Optional Filter** | Alert when heart rate > 150 bpm        |

---

### 8) How It Works

1. Dashboards connect to the **`heart_rate` index**, which is continuously populated by Lambda.
2. The **timestamp field** is used to display the heart rate trend over time.
3. Users can **interactively zoom**, filter time ranges, and apply conditions.
4. Since OpenSearch uses **inverted indexing**, queries and visualizations are fast and efficient.

&nbsp;

**Click Image to Download a sample video of the Live Dashboard**

[![Watch Live Demo](https://github.com/adiman1/liveheartrate/raw/ae07506a38c7b8cb48a4dea78600e1bb44360c1d/Layer%204%20-%20AWS%20Services/images/live_stream_end.png)](https://github.com/adiman1/liveheartrate/raw/e126701b2c4053bde1ce51f4c42d09ace07613ae/OpenSearch%20Dashboard%20Livestream.mp4)

---

### 9) Access Control

- Fine-grained access control was enabled.
- Dashboards are protected with **username/password login**.
- Lambda was authorized via an IAM role with **resource-based access to OpenSearch**.

---

## D) Design Trade-offs & Justifications

-  **No sub-second or 1-second polling**:
  - AWS **Timestream** (best suited for time-series at that granularity) was **not used** cause of the lack of availability for Free-Tier Users.
  - OpenSearch is capable of near real-time ingestion, but:
    -  Achieving **sub-second** streaming would require:
      - High-frequency BLE polling
      - More aggressive Lambda concurrency
      - A time-series store optimized for millisecond ingestion like Timestream or InfluxDB

-  **No Grafana integration**:
  - While OpenSearch can connect to **Grafana**, it was **intentionally avoided** because:
    - All the **services were in ap-south-1 zone** and grafana was unavailable. So to avoid mix of zones.
    - Keep the stack lean
    - Use **OpenSearch Dashboard natively**, since it supports time-series visualizations and filters out of the box

> This setup provides a balanced trade-off: **simple, low-latency, and cost-efficient** real-time visualization without introducing additional dashboarding or storage complexity.

---

## E) Additional Necessary Information

### 1) What is SigV4 (Signature Version 4)?

**SigV4** (Signature Version 4) is AWS's protocol for **securely signing API requests**. It ensures:

- **Authentication**: The caller is who they claim to be.
- **Authorization**: The caller has the right IAM permissions.
- **Integrity**: The request hasn’t been tampered with during transit.

Structure:
- An HMAC-based signature generated using **temporary IAM credentials**.
- A `Host`, `X-Amz-Date`, and `Authorization` header.
- A hashed version of the request body and parameters.

---

### 2) Why SigV4 in Our Live Visualization Flow?

Our architecture uses **Amazon OpenSearch** for real-time visualization, and OpenSearch domains configured with **fine-grained IAM access control** require all HTTP requests to be signed using SigV4.

FGAC (fine-grained IAM access control) - To create a master user for OS Domain and access it via masters ID and password

---

### 3) Where SigV4 Is Used in the Flow

| Component      | Role in SigV4                                                |
|----------------|--------------------------------------------------------------|
| **Lambda**     | Acts as the **caller**. Gets temporary IAM credentials.      |
| **requests_aws4auth** | Signs the `requests.post()` call to OpenSearch using SigV4. |
| **OpenSearch** | Accepts only **signed requests** when IAM-based access control is enabled. |
| **IAM Role**   | Lambda's execution role has the permission to post to OpenSearch. |

---

### 4) Without SigV4?
OpenSearch would **reject all unsigned requests** with a 403 "not authorized" error, even if the data is valid.

---

### 5) Summary

- SigV4 ensures **secure, authenticated, and authorized** communication between your Lambda function and OpenSearch.
- Tools like `requests_aws4auth` make it easy to generate signed HTTP requests using the credentials automatically assumed by Lambda at runtime.

---
