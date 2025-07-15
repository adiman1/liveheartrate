# Layer 4 – AWS Services  

## Section 1: Batched Storage

### Purpose
Store heart rate data from the BLE device in **batch form** for historical analysis, audits, or further processing.

---

### Data Flow Summary

Kinesis Data Stream → Kinesis Firehose → S3 (Parquet)

### Components

| AWS Service           | Role                                                                      |
|-----------------------|---------------------------------------------------------------------------|
| **Kinesis Firehose**  | Buffers streaming data and delivers it to S3 in batches                   |
| **S3 Bucket**         | Stores incoming batched heart rate data in Parquet format                 |

---

## Service 1 - Kinesis Data Firehose 🚰 for Managed Delivery & Conversion

1) Kinesis Data Firehose is a **serverless data delivery service**.
2) It **reads data from Kinesis Data Streams**, **transforms it if needed, buffers it, and delivers it automatically to storage destinations** like Amazon S3.

### 💡 Why Firehose?

- **No manual polling** from KDS — Firehose handles it.
- Converts raw JSON into **Parquet** (efficient columnar format).
- Batches data based on buffer size or time.
- Automatically writes to S3 with timestamp-based paths.

### 🔧 Configuration Summary

| Setting                        | Value                                                                |
|--------------------------------|----------------------------------------------------------------------|
| Delivery Stream Name           | `hr_firehose`                                                        |
| Source                         | Kinesis Stream – `hr-kinesis-stream`                                 |
| Input Format                   | OpenX JSON SerDe                                                     |
| Output Format                  | Apache Parquet                                                       |
| Destination                    | Amazon S3                                                            |
| Target S3 Bucket               | `garmin-hr-s3-bucket`                                                |
| S3 Prefix                      | `heart_rate_data/!{timestamp:yyyy}/!{timestamp:MM}/!{timestamp:dd}/session_!{timestamp:HH-mm-ss}/` |
| Buffer Size                    | 64 MiB                                                               |
| Buffer Interval                | 60 seconds (set max to 900)                                          |
| Time Zone                      | Asia/Calcutta                                                        |

&nbsp;

> **Notes**
> Buffer size - 64 MiB (set lowest, cause our data from KDS is a few mb at max (10 mb at max for a 15 mins run).
> With direct json ingestion – min buffer size can be 1 Mb
> Buffer interval - 60 seconds (set at max value 900, to get a single/couple parquet files in S3 for a 15 min run)

---


