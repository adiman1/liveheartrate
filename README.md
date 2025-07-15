# liveheartrate
1) Pipeline built to **stream real-time heart rate data** from a Garmin smartwatch to the cloud.
2) It reads data over Bluetooth using Python libraries, then uses AWS services to live stream, store, and visualize heart rate data (in real time).
3) The project is explained in Layers. Go through folders in sequence (1 - 4) for E2E Explanation of the Project

&nbsp;

## Architecture Overview

### This project uses a Lambda-like Architecture

This project implements a real time heart rate monitoring pipeline using a simplified **Lambda Architecture** pattern.

Lambda Architecture is a data-processing design that combines:
- **Batch processing**: handle and store large volume data
- **Stream processing**: for real time, low latency insights

This project applies the same principle using AWS services.

---

## Components Mapping

| Lambda Layers     | Implementation Used                                                                         |
|-------------------|---------------------------------------------------------------------------------------------|
| **Batch Layer**   | ✅ **Amazon S3 via Firehose**: stores all raw heart rate data                               |
|                   | ✅ **AWS Glue + Athena**: for historical / Ad Hoc querying                                  |
| **Speed Layer**   | ✅ **AWS Lambda**: processes real time records from Kinesis Stream                          |
|                   | ✅ **Amazon OpenSearch**: receives real-time processed data, acts as TimeSeries DB          |
| **Serving Layer** | ✅ **OpenSearch Dashboard**: unified analytics and alerts                                   |

---

## Data Flow

```
plaintext
Garmin Smartwatch (BLE)
↓
PC via Bleak (Python)
↓
AWS Kinesis Data Stream
├──→ AWS Lambda → OpenSearch (real-time index)
└──→ Firehose → S3 → Glue Catalog → Athena (historical data)
```
---

![High Level Data Flow over Tools](https://github.com/adiman1/liveheartrate/blob/0a2f8de1a3f68ac8a19e7b2890908e6a8047af2a/images/aws%20flow_page-0001.JPG)
