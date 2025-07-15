# Layer 4 – AWS Services 

## Solution for Batched Storage

### 1) Purpose
Store heart rate data from the BLE device in **batch form** for historical analysis, audits, or further processing.

---

### 2) Data Flow Summary

Kinesis Data Stream → Kinesis Firehose → S3 (Parquet)

### Components

| AWS Service           | Role                                                                      |
|-----------------------|---------------------------------------------------------------------------|
| **Kinesis Firehose**  | Buffers streaming data and delivers it to S3 in batches                   |
| **S3 Bucket**         | Stores incoming batched heart rate data in Parquet format                 |

---

## Service 1 - 🚰 Kinesis Data Firehose for Managed Delivery & Conversion

1) Kinesis Data Firehose is a **serverless data delivery service**.
2) It **reads data from Kinesis Data Streams**, **transforms it if needed, buffers it, and delivers it automatically to storage destinations** like Amazon S3.

### 1) Why Firehose?

- **No manual polling** from KDS — Firehose handles it.
- Converts raw JSON into **Parquet** (efficient columnar format).
- Batches data based on buffer size or time.
- Automatically writes to S3 with timestamp-based paths.

### 2) Configuration Summary

| Setting                        | Value                                                                |
|--------------------------------|----------------------------------------------------------------------|
| Delivery Stream Name           | `hr_firehose`                                                        |
| Source                         | Kinesis Stream – `hr-kinesis-stream`                                 |
| Input Format                   | OpenX JSON SerDe                                                     |
| Output Format                  | Apache Parquet                                                       |
| Destination                    | Amazon S3                                                            |
| Target S3 Bucket               | `garmin-hr-s3-bucket`                                                |
| S3 Prefix                      | `heart_rate_data/!{timestamp:yyyy}/!{timestamp:MM}/!{timestamp:dd}/session_!{timestamp:HH-mm-ss}/` |
| Buffer Size                    | 64 MB                                                                |
| Buffer Interval                | 60 seconds (set max to 900)                                          |
| Time Zone                      | Asia/Calcutta                                                        |


> **Notes**
> 1) Buffer size - 64 MB (set lowest, cause our data from KDS is a few mb at max (10 mb at max for a 15 mins run).
> 2) With direct JSON ingestion – min buffer size can be set at 1 mb
> 3) Buffer interval - 60 seconds (set at max value 900, to get a single/couple parquet files in S3 for a 15 min run)

---

## Service 2 - 🪣 Simple Storage Service (S3)
1) Amazon S3 is an **object storage service** that serves as the **landing zone** for processed and batched heart rate data.
2) In our case, S3 is the landing spot for our batched data from Firehose.
3) Also, it can store a plethora of formats.

### 1) S3 Folder Structure

1) First create a Bucket.
2) In our case, we created one called garmin-hr-s3-bucket
3) If you observe this was given as the name for the Firehose Target. **Hence create S3 object first.**
4) Also you can observe a Firehose config called **S3 Prefix**. This is used to partition the incoming Firehose data.
   
**Why the need for partitions:**
- The structure is **timestamp-partitioned** for easy accessibility and readability.  
- It supports **efficient querying** using **Athena or AWS Glue**.

```plaintext
garmin-hr-s3-bucket/
└── heart_rate_data/
    └── 2025/
        └── 07/
            └── 13/
                └── session_21-25-19/
                    └── part-*.parquet
```

**Basically this prefix was used to represent the date-hour-second at which we recorded a session.**

### 2) S3 Folder Structure - Image

Observe the top left corner, you can see the structure created by firehose.

![S3 Folder Structure](https://github.com/adiman1/liveheartrate/blob/b9176c37a0a7328327bd0fd3cb86c54ba379116c/Layer%204%20-%20AWS%20Services/images/S3%20Folder%20Structure.png)

&nbsp;

## ⏱ Firehose Timestamp & Buffering: How They Impact S3 Partitioning

Lets see how Firehose determines S3 folder structure using ingestion time and how buffer settings influence the number of partitions.

---

### 1) Ingestion Timestamp vs Data Timestamp

Each record sent from your Python BLE script includes a field like:

```json
  { "timestamp": "2025-07-15T17:10:33", "heart_rate": 89 }
```

1) This timestamp is part of the data payload, but Firehose ignores it for partitioning.
2) Firehose instead uses the record ingestion time (i.e., when Firehose receives it) for substituting placeholders in your configured S3 prefix:
   - heart_rate_data/!{timestamp:yyyy}/!{timestamp:MM}/!{timestamp:dd}/session_!{timestamp:HH-mm-ss}/

### 2) How Firehose Buffer Settings Affect Delivery

We know our Firehose Buffer Config is:

| Setting                        | Value                                                                |
|--------------------------------|----------------------------------------------------------------------|
| Buffer Size                    | 64 MB                                                                |
| Buffer Interval                | 60 seconds                                                           |

### 3) How the Buffer Interval affects Partition Count

Example: 
- A 15-minute session (set in py code)
- With 60-second buffer interval (in Firehose),
- Implies a folder created in S3 **every 60 sec/1 min**

** Let’s assume your run started at - 2025/07/15/17:10:00**

```plaintext
garmin-hr-s3-bucket/
└── heart_rate_data/
    └── 2025/
        └── 07/
            └── 15/
                └── session_17-10-00/
                └── session_17-11-00/
                └── session_17-12-00/
                └── session_17-13-00/
                └── session_17-14-00/
                └── session_17-15-00/
                └── session_17-16-00/
                └── session_17-17-00/
                └── session_17-18-00/
                └── session_17-19-00/
                └── session_17-20-00/
                └── session_17-21-00/
                └── session_17-22-00/
                └── session_17-23-00/
                └── session_17-24-00/
```

The same pattern can be seen in the image (blue highlighted section) attached above in S3 Folder Structure.

Parquet Files can be seen in each session folder.

### 4) Why S3

- S3 objects live forever unless deleted or transitioned via lifecycle rules.
- You pay for storage, requests, and transfers separately.
- Optimize costs using:
  - Fewer, larger files
  - Appropriate storage class transitions
  - Lifecycle policies for cleanup

---









