# Mobile App Streaming Integration Guide

## 📱 Overview

This guide explains how to stream health data from wearable devices to mobile apps and then to the Health Tracker application using various local communication technologies.

---

## 🔄 Data Flow Architecture

```
┌─────────────────┐         ┌──────────────┐         ┌──────────────────┐
│  Wearable       │────────▶│  Mobile App  │────────▶│  Health Tracker  │
│  Device         │  BLE/   │  (Gateway)   │  HTTP/  │  Web Application │
│  (Sensor)       │  NFC/   │              │  WebSocket│                 │
│                 │  WiFi   │              │         │                  │
└─────────────────┘         └──────────────┘         └──────────────────┘
     Step 1                      Step 2                    Step 3
  Local Transfer            Data Processing          Cloud Storage
```

---

## 🛠️ Technology Options

### 1. Bluetooth Low Energy (BLE) - **RECOMMENDED**

#### How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                    BLE Communication Flow                   │
└─────────────────────────────────────────────────────────────┘

┌─────────────┐                    ┌─────────────┐
│   Device    │                    │  Mobile App │
│  (Peripheral)│                    │  (Central)  │
└──────┬──────┘                    └──────┬──────┘
       │                                   │
       │ 1. Advertise Service UUID         │
       │──────────────────────────────────▶│
       │                                   │
       │ 2. Scan & Discover                │
       │◀──────────────────────────────────│
       │                                   │
       │ 3. Connect Request                │
       │──────────────────────────────────▶│
       │                                   │
       │ 4. Connection Established         │
       │◀──────────────────────────────────│
       │                                   │
       │ 5. Read/Write Characteristics     │
       │◀─────────────────────────────────▶│
       │                                   │
       │ 6. Notify (Stream Data)           │
       │──────────────────────────────────▶│
       │                                   │
       │ 7. Disconnect                     │
       │◀──────────────────────────────────│
```

#### Technical Details

**Range:** Up to 100 meters (line of sight)  
**Power Consumption:** Very Low (battery-friendly)  
**Data Rate:** Up to 1 Mbps  
**Frequency:** 2.4 GHz ISM band

**BLE GATT Structure:**
```
Device
├── Service (e.g., Heart Rate Service)
│   ├── Characteristic (Heart Rate Measurement)
│   │   ├── Value: 72 bpm
│   │   ├── Descriptor: Update Interval
│   │   └── Properties: Read, Notify
│   └── Characteristic (Body Sensor Location)
└── Service (Battery Service)
    └── Characteristic (Battery Level)
```

#### Implementation Steps

**Step 1: Device Setup (Peripheral)**
```javascript
// Device broadcasts these services
const heartRateService = {
    uuid: '0000180d-0000-1000-8000-00805f9b34fb',
    characteristics: {
        measurement: '00002a37-0000-1000-8000-00805f9b34fb',
        bodyLocation: '00002a38-0000-1000-8000-00805f9b34fb'
    }
};
```

**Step 2: Mobile App Setup (Central)**
```javascript
// React Native BLE Example
import { BleManager } from 'react-native-ble-plx';

const manager = new BleManager();

// Scan for devices
manager.startDeviceScan(
    [heartRateService.uuid],
    null,
    (error, device) => {
        if (error) {
            console.error(error);
            return;
        }
        // Connect to device
        device.connect()
            .then(device => {
                return device.discoverAllServicesAndCharacteristics();
            })
            .then(device => {
                // Subscribe to notifications
                return device.monitorCharacteristicForService(
                    heartRateService.uuid,
                    heartRateService.characteristics.measurement,
                    (error, characteristic) => {
                        if (characteristic?.value) {
                            const data = parseHeartRate(characteristic.value);
                            sendToHealthTracker(data);
                        }
                    }
                );
            });
    }
);
```

**Step 3: Data Processing**
```javascript
function parseHeartRate(hexValue) {
    const bytes = hexToBytes(hexValue);
    const flags = bytes[0];
    const heartRate = flags & 0x01 ? 
        (bytes[1] | (bytes[2] << 8)) : bytes[1];
    
    return {
        heartRate: heartRate,
        timestamp: new Date().toISOString(),
        sensorLocation: bytes[3] || 'chest'
    };
}
```

**Step 4: Send to Health Tracker**
```javascript
async function sendToHealthTracker(data) {
    const response = await fetch('https://your-app.railway.app/api/stream/health-data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authToken}`
        },
        body: JSON.stringify({
            device_id: deviceId,
            device_type: 'heart_rate_monitor',
            data: data,
            timestamp: new Date().toISOString()
        })
    });
}
```

#### Advantages
✅ Low power consumption  
✅ Works with most modern devices  
✅ Real-time data streaming  
✅ No internet required for device-to-mobile

#### Disadvantages
❌ Limited range (~10-100m)  
❌ Requires pairing  
❌ Platform-specific implementations

---

### 2. Near Field Communication (NFC)

#### How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                    NFC Communication Flow                   │
└─────────────────────────────────────────────────────────────┘

┌─────────────┐                    ┌─────────────┐
│   Device    │                    │  Mobile App │
│  (NFC Tag)  │                    │  (Reader)   │
└──────┬──────┘                    └──────┬──────┘
       │                                   │
       │ 1. Device in range (< 4cm)        │
       │                                   │
       │ 2. NFC Field Activated            │
       │◀──────────────────────────────────│
       │                                   │
       │ 3. Tag Responds with Data         │
       │──────────────────────────────────▶│
       │                                   │
       │ 4. Data Read Complete             │
       │                                   │
       │ 5. Process & Upload                │
       │                                   │
```

#### Technical Details

**Range:** Up to 4 cm (very short range)  
**Power:** Passive (device doesn't need battery)  
**Data Rate:** 106-848 kbps  
**Frequency:** 13.56 MHz

**NFC Data Format (NDEF):**
```
NDEF Message
├── Record 1: Health Data
│   ├── Type: "application/vnd.health.data"
│   ├── Payload: {"heartRate": 72, "timestamp": "..."}
│   └── Flag: MB (Message Begin)
└── Record 2: Device Info
    ├── Type: "text/plain"
    ├── Payload: "Device: BP Monitor, Model: XYZ"
    └── Flag: ME (Message End)
```

#### Implementation Steps

**Step 1: Device Setup (NFC Tag)**
```javascript
// Device writes NDEF message
const healthData = {
    type: 'blood_pressure',
    systolic: 120,
    diastolic: 80,
    timestamp: Date.now()
};

const ndefMessage = [
    {
        id: [],
        type: 'application/vnd.health.data',
        payload: JSON.stringify(healthData),
        tnf: Ndef.TNF_MIME_MEDIA
    }
];

// Write to NFC tag
NfcManager.writeNdefMessage(ndefMessage);
```

**Step 2: Mobile App Setup (NFC Reader)**
```javascript
// React Native NFC Example
import NfcManager, { NfcTech, Ndef } from 'react-native-nfc-manager';

async function readNfcTag() {
    try {
        await NfcManager.requestTechnology(NfcTech.Ndef);
        
        const tag = await NfcManager.getTag();
        const ndefMessage = tag.ndefMessage;
        
        if (ndefMessage && ndefMessage.length > 0) {
            const record = ndefMessage[0];
            const payload = Ndef.text.decodePayload(record.payload);
            const healthData = JSON.parse(payload);
            
            // Send to Health Tracker
            await sendToHealthTracker(healthData);
        }
    } catch (error) {
        console.error('NFC read error:', error);
    } finally {
        NfcManager.cancelTechnologyRequest();
    }
}

// Start listening
NfcManager.start();
NfcManager.setEventListener('TagDiscovered', readNfcTag);
```

#### Advantages
✅ Very secure (requires close proximity)  
✅ No pairing required  
✅ Works with passive devices  
✅ Fast data transfer

#### Disadvantages
❌ Very short range (4cm)  
❌ Requires physical contact/tap  
❌ Not suitable for continuous streaming  
❌ Limited data capacity

---

### 3. WiFi Direct / WiFi P2P

#### How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                 WiFi Direct Communication Flow              │
└─────────────────────────────────────────────────────────────┘

┌─────────────┐                    ┌─────────────┐
│   Device    │                    │  Mobile App │
│  (Group Owner)│                    │  (Client)   │
└──────┬──────┘                    └──────┬──────┘
       │                                   │
       │ 1. Create P2P Group               │
       │                                   │
       │ 2. Broadcast Service Discovery    │
       │──────────────────────────────────▶│
       │                                   │
       │ 3. Device Discovery               │
       │◀──────────────────────────────────│
       │                                   │
       │ 4. Connection Request             │
       │──────────────────────────────────▶│
       │                                   │
       │ 5. IP Assignment (192.168.49.x)    │
       │◀──────────────────────────────────│
       │                                   │
       │ 6. TCP/HTTP Connection            │
       │◀─────────────────────────────────▶│
       │                                   │
       │ 7. Stream Data via HTTP/WebSocket │
       │◀─────────────────────────────────▶│
```

#### Technical Details

**Range:** Up to 200 meters  
**Power:** Medium-High  
**Data Rate:** Up to 250 Mbps  
**Frequency:** 2.4 GHz / 5 GHz

**WiFi Direct Network Topology:**
```
                    ┌─────────────┐
                    │  Group Owner │
                    │   (Device)   │
                    └──────┬───────┘
                           │
            ┌──────────────┼──────────────┐
            │              │              │
      ┌─────▼─────┐  ┌─────▼─────┐  ┌─────▼─────┐
      │  Client 1 │  │  Client 2 │  │  Client 3 │
      │ (Mobile)  │  │ (Mobile)  │  │ (Tablet)  │
      └───────────┘  └───────────┘  └───────────┘
```

#### Implementation Steps

**Step 1: Device Setup (Group Owner)**
```python
# Python example for device
import socket
import json

# Create WiFi Direct group
def create_wifi_direct_group():
    # Device creates P2P group
    # SSID: "HealthDevice_ABC123"
    # Password: "HealthPass123"
    pass

# Start HTTP server
def start_data_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('192.168.49.1', 8080))
    server.listen(5)
    
    while True:
        client, addr = server.accept()
        # Send health data
        data = {
            'heart_rate': 72,
            'timestamp': datetime.now().isoformat()
        }
        client.send(json.dumps(data).encode())
        client.close()
```

**Step 2: Mobile App Setup (Client)**
```javascript
// React Native WiFi Direct (requires native module)
import WifiManager from 'react-native-wifi-manager';

async function connectToDevice() {
    // Discover WiFi Direct devices
    const devices = await WifiManager.discoverPeers();
    
    // Connect to health device
    const device = devices.find(d => d.deviceName.includes('HealthDevice'));
    await WifiManager.connectToPeer(device.deviceAddress, 'HealthPass123');
    
    // Get assigned IP
    const ip = await WifiManager.getIP();
    
    // Connect to device's HTTP server
    const response = await fetch(`http://192.168.49.1:8080/data`, {
        method: 'GET'
    });
    
    const healthData = await response.json();
    await sendToHealthTracker(healthData);
}
```

#### Advantages
✅ High data rate  
✅ Good range  
✅ Can connect multiple devices  
✅ Standard TCP/IP protocols

#### Disadvantages
❌ Higher power consumption  
❌ More complex setup  
❌ May disconnect from internet  
❌ Platform support varies

---

## 📊 Complete Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│              Complete Streaming Data Flow                       │
└─────────────────────────────────────────────────────────────────┘

                    ┌──────────────┐
                    │ Wearable     │
                    │ Device       │
                    │ (Sensor)     │
                    └──────┬───────┘
                           │
                           │ Local Communication
                           │ (BLE/NFC/WiFi Direct)
                           │
                    ┌──────▼───────┐
                    │              │
                    │  Mobile App  │
                    │  (Gateway)   │
                    │              │
                    │  ┌────────┐ │
                    │  │ Buffer │ │
                    │  │ Queue  │ │
                    │  └────┬───┘ │
                    │       │     │
                    │  ┌────▼───┐ │
                    │  │ Process│ │
                    │  │ & Valid│ │
                    │  └────┬───┘ │
                    └──────┼──────┘
                           │
                           │ Internet Connection
                           │ (HTTP/WebSocket)
                           │
                    ┌──────▼───────┐
                    │              │
                    │ Health Tracker│
                    │ API Endpoint │
                    │              │
                    │  ┌────────┐  │
                    │  │ Validate│ │
                    │  └────┬───┘  │
                    │       │      │
                    │  ┌────▼───┐  │
                    │  │ Database│  │
                    │  └────────┘  │
                    └───────────────┘
```

---

## 🔌 API Endpoints for Mobile App

### Streaming Endpoint

**POST** `/api/stream/health-data`

**Request Body:**
```json
{
    "device_id": "fitbit_abc123",
    "device_type": "heart_rate_monitor",
    "connection_type": "ble",
    "data": {
        "heart_rate": 72,
        "timestamp": "2025-01-15T10:30:00Z"
    },
    "metadata": {
        "battery_level": 85,
        "signal_strength": -45
    }
}
```

**Response:**
```json
{
    "success": true,
    "message": "Data received",
    "record_id": 12345
}
```

### Batch Streaming Endpoint

**POST** `/api/stream/batch`

**Request Body:**
```json
{
    "device_id": "fitbit_abc123",
    "device_type": "fitness_tracker",
    "connection_type": "ble",
    "data_points": [
        {
            "heart_rate": 72,
            "steps": 1000,
            "timestamp": "2025-01-15T10:30:00Z"
        },
        {
            "heart_rate": 75,
            "steps": 1050,
            "timestamp": "2025-01-15T10:31:00Z"
        }
    ]
}
```

### WebSocket Streaming Endpoint

**WS** `/api/stream/ws`

**Connection:**
```javascript
const ws = new WebSocket('wss://your-app.railway.app/api/stream/ws?token=YOUR_TOKEN');

ws.onopen = () => {
    // Send data continuously
    setInterval(() => {
        ws.send(JSON.stringify({
            device_id: deviceId,
            data: currentHealthData
        }));
    }, 1000); // Every second
};

ws.onmessage = (event) => {
    const response = JSON.parse(event.data);
    console.log('Server response:', response);
};
```

---

## 📱 Mobile App Architecture

### React Native Example Structure

```
Mobile Health Gateway App
├── src/
│   ├── ble/
│   │   ├── BLEManager.js          # BLE connection management
│   │   ├── DeviceScanner.js       # Device discovery
│   │   └── DataParser.js          # Parse BLE data
│   ├── nfc/
│   │   ├── NFCManager.js          # NFC reading
│   │   └── NDEFParser.js          # Parse NDEF messages
│   ├── wifi/
│   │   ├── WiFiDirectManager.js   # WiFi Direct connection
│   │   └── DataFetcher.js         # Fetch from device
│   ├── api/
│   │   ├── HealthTrackerAPI.js    # API client
│   │   └── WebSocketClient.js     # WebSocket connection
│   ├── storage/
│   │   ├── LocalBuffer.js         # Local data buffer
│   │   └── QueueManager.js         # Queue management
│   └── screens/
│       ├── DeviceScanScreen.js    # Scan for devices
│       ├── ConnectionScreen.js    # Manage connections
│       └── StreamingScreen.js     # Monitor streaming
└── package.json
```

### Key Components

**1. Connection Manager**
```javascript
class ConnectionManager {
    constructor() {
        this.connections = new Map();
        this.dataQueue = [];
    }
    
    async connectBLE(deviceId) {
        const connection = await BLEManager.connect(deviceId);
        connection.on('data', (data) => {
            this.queueData(data);
        });
        this.connections.set(deviceId, connection);
    }
    
    queueData(data) {
        this.dataQueue.push({
            ...data,
            timestamp: Date.now()
        });
        this.processQueue();
    }
    
    async processQueue() {
        while (this.dataQueue.length > 0) {
            const data = this.dataQueue.shift();
            await HealthTrackerAPI.sendData(data);
        }
    }
}
```

**2. Data Buffer**
```javascript
class DataBuffer {
    constructor(maxSize = 1000) {
        this.buffer = [];
        this.maxSize = maxSize;
    }
    
    add(data) {
        this.buffer.push(data);
        if (this.buffer.length > this.maxSize) {
            this.buffer.shift(); // Remove oldest
        }
    }
    
    flush() {
        const data = [...this.buffer];
        this.buffer = [];
        return data;
    }
}
```

---

## 🔄 Real-Time Streaming Flow

```
Time: 00:00:00
Device ──[HR: 72]──▶ Mobile ──[Buffer]──▶ Queue ──[HTTP POST]──▶ API ──[DB]──▶ Success

Time: 00:00:01
Device ──[HR: 73]──▶ Mobile ──[Buffer]──▶ Queue ──[HTTP POST]──▶ API ──[DB]──▶ Success

Time: 00:00:02
Device ──[HR: 74]──▶ Mobile ──[Buffer]──▶ Queue ──[HTTP POST]──▶ API ──[DB]──▶ Success

... Continuous streaming ...
```

---

## 🎯 Implementation Priority

### Phase 1: BLE Integration (Week 1-2)
1. Set up React Native app
2. Implement BLE scanning
3. Connect to common devices (Fitbit, heart rate monitors)
4. Stream data to API
5. **Cost:** $500 - $1,000

### Phase 2: NFC Integration (Week 3)
1. Add NFC reading capability
2. Support passive devices
3. One-tap data transfer
4. **Cost:** $200 - $400

### Phase 3: WiFi Direct (Week 4)
1. Implement WiFi Direct
2. Support high-bandwidth devices
3. Multi-device support
4. **Cost:** $400 - $800

### Phase 4: Optimization (Week 5-6)
1. Offline buffering
2. Batch uploads
3. Error handling & retry
4. Battery optimization
5. **Cost:** $300 - $600

**Total Development Cost:** $1,400 - $2,800

---

## 📋 Mobile App Requirements

### Platform Support
- ✅ iOS 13+ (BLE, NFC)
- ✅ Android 5.0+ (BLE, NFC, WiFi Direct)
- ⚠️ iOS WiFi Direct (Limited support)

### Permissions Required

**iOS:**
- `NSBluetoothPeripheralUsageDescription`
- `NSNFCReaderUsageDescription`
- `NSLocationWhenInUseUsageDescription` (for BLE)

**Android:**
- `BLUETOOTH`
- `BLUETOOTH_ADMIN`
- `BLUETOOTH_SCAN`
- `BLUETOOTH_CONNECT`
- `NFC`
- `ACCESS_WIFI_STATE`
- `CHANGE_WIFI_STATE`

---

## 🔐 Security Considerations

### Device Authentication
```javascript
// Generate device certificate
const deviceCert = generateCertificate({
    deviceId: deviceId,
    publicKey: devicePublicKey,
    timestamp: Date.now()
});

// Verify on server
function verifyDevice(deviceId, signature, data) {
    const publicKey = getDevicePublicKey(deviceId);
    return verifySignature(publicKey, signature, data);
}
```

### Data Encryption
```javascript
// Encrypt data before transmission
const encryptedData = encrypt(healthData, serverPublicKey);

// Server decrypts
const decryptedData = decrypt(encryptedData, serverPrivateKey);
```

---

## 📊 Performance Metrics

### Expected Performance

| Technology | Latency | Throughput | Battery Impact |
|------------|---------|------------|----------------|
| BLE        | 10-50ms | 1 Mbps     | Low            |
| NFC        | <10ms   | 848 kbps   | Very Low       |
| WiFi Direct| 5-20ms  | 250 Mbps   | High           |

### Optimization Strategies

1. **Batch Uploads:** Collect data for 30-60 seconds, upload in batches
2. **Compression:** Compress data before transmission
3. **Delta Updates:** Only send changed values
4. **Smart Buffering:** Buffer when offline, upload when online

---

## 🚀 Quick Start Guide

### For Developers

1. **Clone Mobile App Template**
   ```bash
   git clone https://github.com/your-org/health-mobile-gateway
   cd health-mobile-gateway
   npm install
   ```

2. **Configure API Endpoint**
   ```javascript
   // config.js
   export const API_ENDPOINT = 'https://your-app.railway.app';
   export const API_TOKEN = 'your-api-token';
   ```

3. **Run on Device**
   ```bash
   # iOS
   npx react-native run-ios
   
   # Android
   npx react-native run-android
   ```

4. **Test Connection**
   - Enable Bluetooth on device
   - Scan for health devices
   - Connect and start streaming

---

## 📚 Additional Resources

- **BLE Specification:** https://www.bluetooth.com/specifications/
- **NFC Forum:** https://nfc-forum.org/
- **WiFi Direct Spec:** https://www.wi-fi.org/discover-wi-fi/wi-fi-direct
- **React Native BLE:** https://github.com/dotintent/react-native-ble-plx
- **React Native NFC:** https://github.com/whitedogg13/react-native-nfc-manager

---

*Last Updated: January 2025*

