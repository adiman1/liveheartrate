# Layer 1 – Source: Garmin Smartwatch via BLE

## 1. What is Garmin?

[Garmin](https://www.garmin.com/) is a popular brand of smartwatches and fitness trackers that monitor real-time physiological data such as:

- Heart rate  
- Blood oxygen (SpO₂)  
- Stress levels  
- Steps, sleep, and more  

Using a feature called **Broadcast HR**, Garmin can transmit heart rate data to external devices in real time.

Garmin uses **Bluetooth Low Energy (BLE)** protocol for this

---

## 2. What is BLE?

**Bluetooth Low Energy (BLE)** is a lightweight wireless communication standard optimized for:

- Low power consumption  
- Transfering small, periodic data packets of data over short distances
- Applications in wearables and IoT devices   

It has 2 parts and In our setup:

- **Garmin** is the **peripheral/server**
- **PC with Python** is the **central/client**

---

### 2.1 BLE Roles

| Role       | Device                   |
|------------|--------------------------|
| Peripheral | Garmin Smartwatch        |
| Central    | PC using Python          |

---

### 2.2 BLE GATT Structure

BLE communication uses somtething called the **Generic Attribute Profile (GATT)** to define how data is structured and exchanged over BLE.

**Example GATT Profile for our HR Case**

 
├── Service: Heart Rate Service (`0x180D`)  
│   └── Characteristic: Heart Rate Measurement (`0x2A37`)  
│       └── Properties: ['notify']  
│           └── Value: e.g., Heart Rate = 90 bpm

When a characteristic supports `notify`, the server/device pushes updates to the client whenever the value changes — perfect for real-time monitoring.

Basically Changing/Continuous Heart rate is **pushed** to our PC on we are subscribed to the garmin device and the service (i.e) Heart Rate Service (0x180D).

Each value in the GATT structure is uniquely identified using a **UUID (Universally Unique Identifier)**. 

The GATT profiles and UUIDs are standards assigned by the **Bluetooth SIG (Special Interest Group)** and are supported by most smartwatches.

---

### 2.3 UUIDs Used

| Component              | UUID (Short) | Full UUID                                      |
|------------------------|--------------|------------------------------------------------|
| Heart Rate Service     | `0x180D`     | `0000180d-0000-1000-8000-00805f9b34fb`         |
| Heart Rate Measurement | `0x2A37`     | `00002a37-0000-1000-8000-00805f9b34fb`         |

These ID's are the one used to subscribe for relevant data of the device. 

In our case Heart Rate Services and Notifications

---

## 3. Data Format (Heart Rate Characteristic `0x2A37`)

Garmin sends **binary packets** with the heart rate and optional data fields when subscribed to the `Heart Rate Measurement` characteristic.

Say it sends an example packet with say two 8-bit Binary bytes:  

- **Byte 0**: 00010100
- **Byte 1**: 01011010

> **Notes**:  
> 1. Each bit is either 0 or 1  
> 2. Bits in a byte are read from **right to left**

According to the SIG specs for (Heart Rate Characteristic/UUID - `0x2A37`):

- **Byte 0**   → Flags  
- **Byte 1–2** → Heart Rate Value  
- **Byte 3–4** → Energy Expended Value
- **Byte 5+**  → RR-Interval (an measurement which tells the time between each heart beat)

---

### 3.1 Byte 0 – Flags

Flags are indicators that show whether optional attributes are present.  

Since there are 8 bits, each one signifies the presence/absence of a feature.

Therfore the SIG Defined flag attributes for each bit in Byte 0 are

| Bit | Meaning                                             |
|-----|-----------------------------------------------------|
| 0   | Heart Rate format: 8-bit or 16-bit                  |
| 1   | Sensor contact detected on skin (yes/no)            |
| 2   | Sensor contact feature supported (yes/no)           |
| 3   | Energy expended value present (yes/no)              |
| 4   | RR Interval present (yes/no)                        |
| 5–7 | Reserved                                            |

> Therefore in our Byte 0 - `00010100`:  

<pre>
0 0 0 1 0 1 0 0
│ │ │ │ │ │ │ └─ Heart Rate Format: 8-bit (0)
│ │ │ │ │ │ └───── Sensor Contact Detected: No (0).
│ │ │ │ │ └───────── Sensor Contact Feature Supported: Yes (1)
│ │ │ │ └───────────── Energy Expended Present: No (0)
│ │ │ └───────────────── RR Interval Present: Yes (1)
│ │ └───────────────────── Reserved
│ └───────────────────────── Reserved
└───────────────────────────── Reserved
</pre>

---

### 3.2 Byte 1 – Heart Rate Value

Byte 1 = `01011010`

This Byte 1 binary value represents the actual **Heart Rate (HR)** in beats per minute.

Here each bit has a power-of-2 value as per SIG definition for Byte 1:

| Bit Position (index) | 7   | 6  | 5  | 4  | 3  | 2  | 1  | 0  |
|----------------------|-----|----|----|----|----|----|----|----|
| Power of 2           | 128 | 64 | 32 | 16 | 8  | 4  | 2  | 1  |

And the breakdown of the byte:

| Bit Position (index) | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
|----------------------|---|---|---|---|---|---|---|---|
| Bit Value (binary)   | 0 | 1 | 0 | 1 | 1 | 0 | 1 | 0 |
| Contribution         | 0 |64 | 0 |16 | 8 | 0 | 2 | 0 |

**Sum** = 64 + 16 + 8 + 2 = **90 bpm**

So, `01011010` = **90 beats per minute**

---

Next, we’ll walk through how to subscribe to this data via Python and forward it to the cloud.

