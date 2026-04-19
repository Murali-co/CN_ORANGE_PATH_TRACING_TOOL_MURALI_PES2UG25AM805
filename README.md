# SDN Path Tracing Tool

An interactive Software-Defined Networking (SDN) tool built using **Mininet** and the **Ryu Controller**. This tool acts as an intelligent learning switch, discovering the network topology, dynamically installing flow rules, and tracing the exact path of packets as they travel across multiple switches.

## 🌟 Features

- **Dynamic MAC Learning**: The controller automatically learns MAC-to-port mappings as packets traverse the network.
- **Reactive Flow Installation**: Installs OpenFlow 1.3 rules directly onto the switches to optimize subsequent communications.
- **Real-Time Path Tracing**: Visually outputs the packet paths directly in the controller console.
- **Path Logging**: Records all traced paths into a `logs/paths.csv` file for later analysis.
- **Custom Topology**: Includes a Mininet topology script simulating a multi-switch, multi-host environment.

---

## 🛠️ Prerequisites

Before running the project, ensure you have the following installed on your Linux environment:
- **Python 3** (and `pip`)
- **Mininet** (`sudo apt install mininet`)
- **Ryu SDN Framework** (`pip3 install ryu`)
- **Eventlet** (`pip3 install eventlet`)

---

## 📂 Project Structure

```text
.
├── controller/
│   └── path_tracer.py     # Ryu Controller App (handles path tracing, MAC learning, and flow installation)
├── topology/
│   └── topology.py        # Mininet custom topology (2 switches, 4 hosts)
├── logs/
│   └── paths.csv          # Output log containing recorded packet paths
├── patch_ryu.py           # Compatibility patch script (if needed for Ryu eventlet setup)
└── README.md              # Project documentation
```

---

## 🔄 How it Works (Workflow)

### System Logic Flowchart

```mermaid
flowchart TD
    A[Start System] --> B[Run Ryu Controller]
    B --> C[Run Mininet Topology]
    C --> D[Switches Connect to Controller]
    D --> E[Install Table-Miss Flow Rule]
    E --> F[Packet Arrives at Switch]
    F --> G{Known Destination MAC?}
    G -- No --> H[Flood Packet]
    H --> F
    G -- Yes --> I[Forward to Correct Port]
    I --> J[Track Path Across Switches]
    J --> K[Display Path in Console]
    K --> L[Install Flow Rule in Switch]
    L --> M[Save Path to CSV Log]
    M --> N[Continue Traffic Monitoring]
    N --> F
```

### Step-by-Step Breakdown

1. **Start System**: The process begins by initializing the required tools.
2. **Run Ryu Controller & Mininet**: The Ryu SDN controller is started, followed by the custom Mininet topology script.
3. **Switches Connect to Controller**: The Open vSwitch (OVS) nodes automatically connect to the Ryu controller.
4. **Install Table-Miss Flow Rule**: The controller installs a default rule on all switches so any unmatched packets are forwarded to the controller.
5. **Packet Arrives at Switch**: When a host generates traffic (like a ping), the switch receives the packet.
6. **Known Destination MAC?**: The controller checks if it has learned the destination MAC address.
   - **No**: The controller commands the switch to **Flood the Packet** out of all ports (except the incoming port).
   - **Yes**: The controller commands the switch to **Forward to the Correct Port**. It then **Tracks the Path**, **Displays it in the Console**, **Installs a Flow Rule** on the switch so future packets bypass the controller, and **Saves the Path to a CSV Log**.
7. **Continue Monitoring**: The system continues to monitor traffic and loops back to handle new incoming packets.

---

## 🚀 Run Instructions

You will need two separate terminal windows to run this tool.

### Terminal 1: Start the Ryu Controller
Start the Ryu controller with the custom path tracing application using your virtual environment:
```bash
~/ryu_venv/bin/ryu-manager controller/path_tracer.py
```
*You should see a message indicating the controller has started and is waiting for switches.*

### Terminal 2: Run the Mininet Topology
In a new terminal, first clear any stale Mininet data, then launch the custom network topology (requires `sudo`):
```bash
sudo mn -c
sudo python3 topology/topology.py
```
*This will create the network (Switches s1, s2 and Hosts h1, h2, h3, h4) and connect them to the controller.*

### Terminal 2: Test the Network
Once the Mininet CLI (`mininet>`) is active, generate traffic to trace the paths:

**Ping all hosts to populate the MAC tables:**
```bash
mininet> pingall
```

**Perform specific host-to-host pings:**
```bash
mininet> h1 ping h4
```

---

## 📊 Expected Output

As you generate traffic in Mininet, switch back to **Terminal 1** (the controller). You will see real-time path traces looking like this:

```
==================================================
 CLEAN SDN PATH TRACING STARTED 
==================================================

[SWITCH CONNECTED] S1
[SWITCH CONNECTED] S2
🔥 PATH: aa:bb → S1 → S2 → cc:dd
[FLOW] S1: 00:00:00:00:00:01 → 00:00:00:00:00:04 via port 3
```

All traced paths are automatically saved to `logs/paths.csv` for auditing and historical analysis.
