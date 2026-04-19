# SDN Path Tracing Tool

## Run Instructions

1. Start Controller:
ryu-manager controller/path_tracer.py

2. Run Topology:
sudo python3 topology/topology.py

3. Test:
mininet> pingall
mininet> h1 ping h4
