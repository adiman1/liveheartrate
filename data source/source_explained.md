# Layer 1 – Source: Garmin Smartwatch via BLE

## What is Garmin?

[Garmin](https://www.garmin.com/) is a popular brand of smartwatches and fitness trackers that monitor real-time physiological data such as:

- Heart rate  
- Blood oxygen (SpO₂)  
- Stress levels  
- Steps, sleep, and more  

Using an option called **Broadcast HR**, we can transmit heart rate data from a Garmin watch to other devices.

Garmin does this via a protocol called **Bluetooth Low Energy (BLE)**, enabling external devices (like a PC or mobile) to connect and stream real-time sensor data.

---

# Understanding BLE and Heart Rate Data Format

## What is BLE?

**Bluetooth Low Energy (BLE)** is a low-power wireless communication protocol designed for transmitting small amounts of data over short distances. It's widely used in wearables and IoT devices such as smartwatches, fitness bands, and medical sensors.

Compared to classic Bluetooth, BLE is optimized for:

- Minimal power consumption  
- Small data packets  
- Periodic transmission (e.g., every 1–2 seconds)  

In this project, **Garmin acts as a BLE peripheral**, and a Python client running on a PC acts as the **BLE central** device that connects and listens for data.

---

## BLE Roles

| Role       | Device                   |
|------------|--------------------------|
| Peripheral | Garmin Smartwatch        |
| Central    | PC using Bleak (Python)  |

---

## BLE GATT Structure

BLE communication is based on the **Generic Attribute Profile (GATT)**. It defines how data is organized and exchanged between devices.

GATT Profile:
Service (e.g., Heart Rate Service)
└── Characteristic (e.g., Heart Rate Measurement)
└── Value (actual data sent from the device)


Each value in the GATT structure is uniquely identified using a **UUID (Universally Unique Identifier)**. These **UUIDs are standards**, assigned by the Bluetooth SIG (Special Interest Group), and are supported by most smartwatches.

There are 8 services and 18 characteristics/values in the Broadcast HR option. The ones we need are below:

---

## UUIDs Used

| Component              | UUID (short) | Full UUID                                      |
|------------------------|--------------|------------------------------------------------|
| Heart Rate Service     | `0x180D`     | `0000180d-0000-1000-8000-00805f9b34fb`         |
| Heart Rate Measurement | `0x2A37`     | `00002a37-0000-1000-8000-00805f9b34fb`         |

---

### Sample GATT Structure

[Service] 0000180d-0000-1000-8000-00805f9b34fb: Heart Rate
├─ [Char] 00002a37-0000-1000-8000-00805f9b34fb (['notify'])

In BLE terms, the `notify` property means the device supports **asynchronous data transmission** when the characteristic value is updated.  
You **subscribe** to it, and whenever your heart rate changes, the device **pushes** the updated data automatically.

This mechanism is:

- **Efficient** – avoids unnecessary polling from the client  
- **Real-time** – updates are sent as soon as the value changes  
- **Low-power** – minimizes energy consumption on both ends  

---

## Data Format

When the PC subscribes to the **Heart Rate Measurement Characteristic (`0x2A37`)**, Garmin sends out **binary packets** containing the current heart rate and optional metadata.

The Heart Rate Measurement (`0x2A37`) spec is defined by Bluetooth as:

- **Byte 0** → Flags  
- **Byte 1–2** → Heart Rate Value (8-bit or 16-bit, depends on bit 0 of flags)  
- **Byte 3–4** → Energy Expended (optional, if bit 3 = 1)  
- **Byte 5+** → RR-Interval (optional, if bit 4 = 1)  

Let's break down what this means.

---

### Byte Data Example

Suppose a BLE heart rate monitor sends the following 2 bytes:
**binary data: 00010100 01011010**


According to the spec:

- **Byte 0** (Flags): `00010100`  
- **Byte 1** (Heart Rate Value): `01011010`  

---

### Byte 0 – Flags Breakdown

First, what is a *flag*?

A **flag** is an indicator to show whether an attribute exists or not. Since there are 8 bits, each bit is assigned to **indicate the presence or absence of an attribute**.

The table below is defined by Bluetooth for **Byte 0** of the Heart Rate Measurement Characteristic (`0x2A37`):

| Bit | Meaning                                             |
|-----|-----------------------------------------------------|
| 0   | Heart Rate value format (8-bit or 16-bit)           |
| 1   | Sensor contact detected on skin (present or not)    |
| 2   | Sensor contact feature supported (yes or no)        |
| 3   | Energy expended field included (yes or no)          |
| 4   | RR Interval values included (yes or no)             |
| 5–7 | Reserved for future use                             |

**Note:**  
1. Each binary bit has two levels – 0 and 1  
2. Bits are read from right to left

So, for Byte 0 = `00010100`:

0 0 0 1 0 1 0 0
│ │ │ │ │ │ │ └─ Heart Rate Format: 8-bit (0)
│ │ │ │ │ │ └───── Sensor Contact Detected: No (0)
│ │ │ │ │ └───────── Sensor Contact Feature Supported: Yes (1)
│ │ │ │ └───────────── Energy Expended Present: No (0)
│ │ │ └───────────────── RR Interval Present: Yes (1)
│ │ └───────────────────── Reserved
│ └───────────────────────── Reserved
└───────────────────────────── Reserved

**Reserved** implies unused or future-configurable fields.

---

### Byte 1 – Heart Rate Value

Byte 1: `01011010`  
This is the actual **Heart Rate (HR)** in binary format.

Each bit has a **power-of-2 weight**, as shown below:

| Bit Position (index) | 7   | 6  | 5  | 4  | 3  | 2  | 1  | 0  |
|----------------------|-----|----|----|----|----|----|----|----|
| Power of 2           | 128 | 64 | 32 | 16 | 8  | 4  | 2  | 1  |

Now let’s decode the byte:

| Bit Position (index) | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
|----------------------|---|---|---|---|---|---|---|---|
| Bit Value (binary)   | 0 | 1 | 0 | 1 | 1 | 0 | 1 | 0 |
| Contribution         | 0 |64 | 0 |16 | 8 | 0 | 2 | 0 |

Sum of contributions = **64 + 16 + 8 + 2 = 90**

So, `01011010` (Byte 1) corresponds to a heart rate of **90 bpm**.

---

Next, we’ll explore how to **access and transform** this binary data via Python.


