# ───────────────────────────────────────────────────────────────────
# File: python_aws_interface.py
# Description: Streams heart rate data from a Garmin device via BLE 
#              and sends a JSON Package with Timestamp and Heart Rate
#              in real-time to AWS Kinesis Data Streams.
# ───────────────────────────────────────────────────────────────────

import boto3
import json
from datetime import datetime
from bleak import BleakClient
import asyncio


# ────────────────────────────────────────────────────────────────────────
# BLE (Bluetooth Low Energy) Configuration - with Data from our Test ipynb
# ────────────────────────────────────────────────────────────────────────
# MAC address of the Garmin device (acts as BLE peripheral)
address = "D4:4A:C4:B0:24:03" 

# UUID for the Heart Rate Measurement Characteristic (0x2A37)
HR_UUID = "00002a37-0000-1000-8000-00805f9b34fb"

# ────────────────────────────────────────────────
# AWS Kinesis Configuration
# ────────────────────────────────────────────────
# Initialize Kinesis client (uses default profile or env vars)
kinesis = boto3.client("kinesis", region_name="ap-south-1")

# Name of the target Kinesis Data Stream we created
KDS_NAME = "hr-kinesis-stream"

# ────────────────────────────────────────────────
# Send Heart Rate Data to AWS Kinesis
# ────────────────────────────────────────────────
def send_to_kinesis(heart_rate):
    """
    Sends a heart rate reading to AWS Kinesis as a JSON record.
    """
    payload = {
        "timestamp": datetime.utcnow().isoformat(),  # UTC timestamp
        "heart_rate": heart_rate                     # Heart rate in bpm
    }

    print("Sending to Kinesis:", payload)

    # Put the JSON payload into the Kinesis stream
    kinesis.put_record(
        StreamName=KDS_NAME,
        Data=json.dumps(payload) + "\n",  # Newline helps downstream tools
        PartitionKey="partition-key"      # Could be device ID for sharding
    )

# ────────────────────────────────────────────────
# Handle BLE Notifications (Callback)
# ────────────────────────────────────────────────
def handle_notification(sender, data):
    """
    Callback function for BLE notifications.
    Extracts heart rate from the byte data and sends it to Kinesis.
    """
    heart_rate = int(data[1])  # 8-bit HR format assumed
    print(f"Heart Rate: {heart_rate} bpm")
    send_to_kinesis(heart_rate)

# ────────────────────────────────────────────────
# BLE Heart Rate Streamer
# ────────────────────────────────────────────────
async def stream_heart_rate():
    """
    Connects to the BLE device, starts heart rate notifications,
    and streams data for a fixed duration.
    """
    async with BleakClient(address) as client:
        await client.start_notify(HR_UUID, handle_notification)
        print("Streaming heart rate for 900 seconds...")
        await asyncio.sleep(900)  # Stream for 15 minutes
        await client.stop_notify(HR_UUID)
        print("Stopped streaming.")

# ────────────────────────────────────────────────
# Main Execution
# ────────────────────────────────────────────────
if __name__ == "__main__":
    asyncio.run(stream_heart_rate())


# ─────────────────────────────────────────────────────────────────────────────
# 📌 Execution Flow - Notes
# 
# 1. Program starts at: 
#       if __name__ == "__main__"
#           → Calls: asyncio.run(stream_heart_rate())
#
# 2. stream_heart_rate():
#       → Connects to BLE device
#       → Starts heart rate notifications
#       → When data arrives, triggers:
#
# 3. handle_notification(sender, data):
#       → Parses heart rate from BLE bytes
#       → Calls:
#
# 4. send_to_kinesis(heart_rate):
#       → Sends heart rate + timestamp to AWS Kinesis Data Stream
#
# This loop continues for 900 seconds (15 minutes), then disconnects and exits.
# ─────────────────────────────────────────────────────────────────────────────

