# Layer 2 – Interface: PC Using Python + Bleak

## 1. Overview

1) The PC serves as the **BLE Central (Client)** device.
2) It scans for the **Garmin peripheral**, connects to it, and subscribes to its **Heart Rate Measurement Characteristic (`0x2A37`)**.
3) Data updates (like heart rate values) are received in real-time.

This is achieved using the **Bleak** library in Python, a modern, asynchronous BLE (Bluetooth Low Energy) client.

---

## 2. Why Bleak?

[**Bleak**](https://github.com/hbldh/bleak) is a lightweight Python library to interface with BLE devices.

- Supports Windows, macOS, and Linux
- Asynchronous API (based on `asyncio`)
- Pure Python – no compilation required
- Ideal for real-time streaming from BLE wearables like Garmin

---

## 2.1 What is async?

**Asynchronous programming** (often called "async") allows a program to perform other operations **without waiting** for a time-consuming task to finish.

In Python, this is done using the `async` and `await` keywords, and is supported by libraries like `asyncio`.

---

![Sync vs Async](https://github.com/adiman1/liveheartrate/blob/a39262d896c32bd8d95a5f75ee47e79f4eb07457/Layer%202%20-%20BLE%20Python%20Interface/images/sync%20vs%20async1.png)

&nbsp;&nbsp;

| Synchronous (blocking)                      | Asynchronous (non-blocking)                  |
|---------------------------------------------|----------------------------------------------|
| Waits for each task to finish fully         | Can handle multiple tasks concurrently       |
| Program halts while waiting (e.g. for data) | Program stays responsive while waiting       |
| Not ideal for I/O heavy tasks               | Ideal for I/O, networking, BLE communication |

---

### Why Async is Needed Here

BLE devices (like Garmin) **send data periodically**, and waiting for each data packet **blocks the entire program** if using normal (synchronous) code.

With **async**:

- The app **subscribes once** to notifications (like heart rate updates)
- allows your program to continue logging, send data to the cloud, and even respond to user's input — all **concurrently**, without waiting for each task to finish before starting the next
- It handles **real-time BLE events** efficiently and smoothly

---

## 3. System Requirements

Before running the interface, ensure the following are installed:

### 3.1 Python & Pip

- Python ≥ 3.8  
- `pip` (Python package manager)

### 3.2 Required Python Packages

Install the necessary libraries:

```bash
pip install bleak
```
---

## 4. Notes

1) Ensure Bluetooth is enabled on the PC.
2) Connect via normal PIN Connection.
3) Run with administrator/root privileges if permission errors occur.
4) Device must have "Broadcast HR" enabled via Garmin settings.
5) In our case, we are parsing only the 8-bit HR (most common) data.
6) For production, extend parsing for Flags, Energy Expended, RR Interval if needed.



