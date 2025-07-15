# AWS Kinesis Data Streams – Key Components

## 1. Stream
- Logical container for data records.
- Made up of one or more **shards**.

## 2. Shard
- Core throughput unit.
- Write: 1 MB/s or 1000 records/s
- Read: 2 MB/s
- More shards = higher parallelism.

## 3. Record
- Unit of data in KDS.
- Contains:
  - `data` (up to 1 MB)
  - `partition key`
  - `sequence number`
    
## 4. Producer
- Sends data into KDS.
- Examples: apps, IoT devices, BLE → Python → AWS SDK.

## 5. Consumer
- Reads data from KDS.
- Types:
  - **Shared fan-out** (default)
  - **Enhanced fan-out** (dedicated throughput)
- Examples: Lambda, KCL app, Firehose.

## 6. Partition Key
- Used to route data to specific shards.
- Enables logical grouping and ordering.

## 7. Sequence Number
- Unique per record in a shard.
- Maintains record ordering.

## 8. Retention Period
- Default: 24 hours.
- Extendable up to 7 or 365 days (extended mode).

# Kinesis Data Streams – Pipeline Overview

| Component         | Description                                                                 |
|-------------------|-----------------------------------------------------------------------------|
| Stream Name       | `hr-data-stream`                                                            |
| Shards            | 1 (can scale as needed)                                                     |
| Record Format     | JSON `{ "timestamp": "...", "heart_rate": ... }`                            |
| Partition Key     | Not explicitly set (using a static or generated default value)              |
| Producer          | Python script using `boto3` + `bleak` to push HR data from Garmin           |
| Consumer          | Firehose, AWS Lambda                                                        |
| Enhanced Fan-out  | Not Enabled                                                                 |
| Retention         | 24 hours (default, extendable)                                              |

Since each json record in our is **Only 2 KB in Size and we get 2 records per sec implying Extremely low Write Throughput.** 

Therfore we have used config for the **Fastest setup and Least compute.**

