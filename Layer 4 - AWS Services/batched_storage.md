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

### Why Firehose?

- **No manual polling** from KDS — Firehose handles it.
- Converts raw JSON into **Parquet** (efficient columnar format).
- Batches data based on buffer size or time.
- Automatically writes to S3 with timestamp-based paths.

### Configuration Summary

| Setting                        | Value                                                                |
|--------------------------------|----------------------------------------------------------------------|
| Delivery Stream Name           | `hr_firehose`                                                        |
| Source                         | Kinesis Stream – `hr-kinesis-stream`                                 |
| Input Format                   | OpenX JSON SerDe                                                     |
| Output Format                  | Apache Parquet                                                       |
| Destination                    | Amazon S3                                                            |
| Target S3 Bucket               | `garmin-hr-s3-bucket`                                                |
| S3 Prefix                      | `heart_rate_data/!{timestamp:yyyy}/!{timestamp:MM}/!{timestamp:dd}/session_!{timestamp:HH-mm-ss}/` |
| Buffer Size                    | 64 MB                                                               |
| Buffer Interval                | 60 seconds (set max to 900)                                          |
| Time Zone                      | Asia/Calcutta                                                        |


> **Notes**
> 1) Buffer size - 64 MB (set lowest, cause our data from KDS is a few mb at max (10 mb at max for a 15 mins run).
> 2) With direct json ingestion – min buffer size can be 1 mb
> 3) Buffer interval - 60 seconds (set at max value 900, to get a single/couple parquet files in S3 for a 15 min run)

---

## Service 2 - Simple Storage Service (S3) 🪣

Amazon S3 is an **object storage service** that serves as the **landing zone** for processed and batched heart rate data.

It can store a plethora of formats.

In our case, S3 is the landing spot for our batched data from Firehose.

### S3 Folder Structure

1) First create a Bucket.
2) In our case, we created one called garmin-hr-s3-bucket
3) If you observe this was given as the name for the Firehose Target. **Hence create S3 object first.**
4) Also you can observe a Firehose config called **S3 Prefix**. This is used to partition the incoming Firehose data.
   
Why the need for partitions:
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

### S3 Folder Structure - Image

Observe the top left corner, you can see the structure created by firehose.

![S3 Folder Structure](https://github.com/adiman1/liveheartrate/blob/b9176c37a0a7328327bd0fd3cb86c54ba379116c/Layer%204%20-%20AWS%20Services/images/S3%20Folder%20Structure.png)









