# Layer 3 – Interface: Python to AWS (Kinesis Data Streams)

## 1. Overview

1) The PC receives **real-time heart rate data** from the Garmin device via BLE and interpreted via **Bleak**.  
2) It forwards each heart rate data point to an **AWS Kinesis Data Stream (KDS)** via **Boto3 SDK**.  
3) This data stream can then be consumed by other services like:

- AWS Lambda (for transformation and routing)
- Firehose (for storage in S3)
- OpenSearch / Grafana (for dashboards)
- Glue / Athena (for querying)

This layer enables **low latency ingestion** and **real time processing** of heart rate telemetry aka **Streaming**

---

## 2. What is Streaming?

**Streaming** is the process of **continuously sending data** as it is generated, rather than waiting for a complete dataset to be available.

---

### 2.1 Traditional (Batch) vs Streaming

| Batch Processing                           | Streaming                                      |
|--------------------------------------------|------------------------------------------------|
| Data is collected and stored first         | Data is sent in real-time                      |
| Processed periodically (e.g. once per hour)| Processed immediately as it arrives            |
| Higher latency                             | Low latency (milliseconds to seconds)          |
| Suited for static reports, logs, etc.      | Ideal for real-time monitoring, alerts, trends |

---

### 2.2 Why We Use Streaming Here

In our case:

- The **Garmin watch** sends heart rate data every few seconds via BLE.
- We want to **capture each reading in real time** on the PC.
- Then we immediately **forward it to AWS Kinesis Data Stream**.

This enables us to forward data instantenously to other AWS cloud services which provide:

- **Live dashboards**
- **Real-time alerts**
- **Continuous storage and analysis**

---

### 2.3 How It Works (High-Level Flow Example)

```plaintext
Garmin (BLE) ──> Bleak Python PC App ──> Kinesis Data Stream ──> Lambda/Firehose/S3/OpenSearch
    (HR)              (boto3)                (real-time)                (processing)
```

---

## 3. Why Kinesis Data Streams?

[**Amazon Kinesis Data Streams**](https://docs.aws.amazon.com/kinesis/) provides a scalable, durable, and real time streaming platform.

### Key Benefits

- **Low-latency streaming** (millisecond-level)
- **Multiple** concurrent consumers  
- Data retention up to **7 days**
- Supports **ordered**, **partitioned** data ingestion  
- Enables real-time ETL, alerting, and monitoring

---

## 4. Requirements

### 4.1 What is boto3?

[**boto3**](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) is the **official AWS SDK (Software Development Kit) for Python**.

It allows your Python code to **interact with AWS services** like:

- Kinesis (Data Streams and Firehose)
- S3 (object storage)
- Lambda (serverless compute)
- DynamoDB, EC2, IAM, and many more

With `boto3`, you can:
- Authenticate using your AWS credentials
- Create and manage AWS resources programmatically
- Send data to Kinesis streams in real time

It acts as a **bridge between Python and AWS APIs**, simplifying cloud integration in your applications.

---

### 4.2 Install boto3

To install `boto3` using pip:

```bash
pip install boto3
```
---

### 4.3 Authentication

Before using boto3, ensure your environment is authenticated.

Simplest method is via an AWS credentials file (~/.aws/credentials), can also use .env files and other methods available

---

## 5. Cloud Prerequisites and Requirements

### 5.1 Prerequisite: Create an AWS Account

To use AWS SDKs, including `boto3`, you must first:

1. Go to [https://aws.amazon.com](https://aws.amazon.com)  
2. Click **Create an AWS Account**
3. Provide:
   - Email address
   - Password
   - Billing information (credit/debit card)
   - Phone verification
4. Choose a support plan (Free Tier is usually enough for development)

### 5.2 Creating a Kinesis Data Stream

- **Name** – `hr-kinesis-stream`
- **Capacity mode** – Provisioned
- **Provisioned shards** – 1
- **Write capacity** – Up to 1 MiB/sec or 1,000 records/sec
- **Read capacity** – Up to 2 MiB/sec (shared by all consumers)

&nbsp;

![Kinesis Stream Configuration](https://raw.githubusercontent.com/adiman1/liveheartrate/ef4d42bac5dd9367d65920eac6519ff6b6322348/Layer%203%20-%20Python%20AWS%20Interface/images/KDS%20Config.png)

&nbsp;

### 5.2.2 KDS Config Explained

Here’s what each of these parameters means:

| Setting            | Description |
|--------------------|-------------|
| **Stream Name**     | Logical name used in boto3 to identify the stream. |
| **Provisioned Mode**| You specify shard count manually (vs. On-Demand which auto-scales). |
| **Shards**          | A shard is a unit of capacity. Each shard allows: <br> ➤ 1,000 writes/sec or 1 MiB/sec write throughput <br> ➤ 2 MiB/sec read throughput |
| **Write Capacity**  | Limited by shard count. For 1 shard, your producer (BLE script) should stay within this limit. |
| **Read Capacity**   | Shared across all consumers (e.g., Lambda, Firehose, OpenSearch). |

> 1 shard is sufficient for single-device heart rate data.  
> You can always **scale up** later by splitting or merging shards.



