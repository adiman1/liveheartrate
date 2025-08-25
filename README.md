# liveheartrate
1) Pipeline built to **stream real-time heart rate data** from a Garmin smartwatch to the cloud.
2) It reads data over Bluetooth using Python libraries, then uses AWS services to live stream, store, and visualize heart rate data (in real time).
   
The project is explained in **Layers**. Go through folders in sequence (1 - 4) for E2E Explanation of the Project

## 1) Architecture Overview

### This project uses a Simplified Lambda-like Architecture

Lambda Architecture is a data-processing design that combines:
- **Batch processing**: handle and store large volume data
- **Stream processing**: for real time, low latency insights

This project applies the same principle using AWS services.

---

## 2) Components Mapping

| Lambda Layers     | Implementation Used                                                                      |
|-------------------|------------------------------------------------------------------------------------------|
| **Batch Layer**   | **Amazon S3 via Firehose**: stores all raw heart rate data                               |
|                   | **AWS Glue + Athena**: for historical / Ad Hoc querying                                  |
| **Speed Layer**   | **AWS Lambda**: processes real time records from Kinesis Stream                          |
|                   | **Amazon OpenSearch**: receives real-time processed data, acts as TimeSeries DB          |
| **Serving Layer** | **OpenSearch Dashboard**: unified analytics and alerts                                   |

---

## 3) Data Flow

![High Level Data Flow over Tools](https://github.com/adiman1/liveheartrate/blob/c67cc49a469c793aba36bf1dd94b44afcfb1fa87/images/Livhrt1.JPG)

## 4) Sample trials

**Click Image to view video of the OpenSearch Live Dashboard**

[![Watch Live Demo](https://github.com/adiman1/liveheartrate/raw/ae07506a38c7b8cb48a4dea78600e1bb44360c1d/Layer%204%20-%20AWS%20Services/images/live_stream_end.png)](https://drive.google.com/file/d/1Qk0ibFtNfzlbsWfBlkbZz4E6CQpzWGjz/view?usp=drive_link)


**Stream Data Plotted in Pandas**

![Streamed Output Plotted in Pandas](https://github.com/adiman1/liveheartrate/blob/7c107e76e499c53edc8f0b55a47ab1c4ee1002a4/images/pandas_output.png)
