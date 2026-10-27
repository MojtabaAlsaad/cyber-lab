# OT/ICS Modbus Lab

This project simulates a simple Modbus TCP industrial control environment for security and network-analysis exercises. It includes a minimal PLC that serves Modbus register data and a client that reads those registers over the network.

## What this project does

- Runs a simulated PLC on port 502 using Python sockets
- Exposes Modbus function code 3 (Read Holding Registers)
- Returns two register values that represent:
  - temperature x 10
  - pressure x 10
- Connects from a separate client container and polls the PLC repeatedly
- Stores packet captures in the `captures/` directory

## Project structure

- `app/plc.py` — simulated PLC server
- `app/client.py` — Modbus client that reads and prints register values
- `compose.yaml` — Docker Compose services and internal network setup
- `Dockerfile` — Python runtime and `tcpdump` installation
- `captures/` — packet capture output directory

## Architecture

The environment is defined in `compose.yaml` with two services:

- `plc` — builds the project and runs the PLC server
- `client` — builds the project and runs the Modbus client

Both services connect to an internal Docker bridge network named `ot-lab-internal`, which isolates traffic from the host network.

The PLC listens on `0.0.0.0:502` and returns a small set of registers. The client connects to `plc:502` and reads 2 registers at a time using Modbus TCP.

## Run the lab

From the project root, start the environment:

```bash
docker compose up -d plc
```

This will start both containers and print the simulated PLC activity and client read results.

To stop and remove the containers:

```bash
docker compose down
```

## Optional traffic capture

The client container has `NET_RAW` enabled and the image includes `tcpdump`, so you can capture live Modbus traffic manually:

```bash
docker compose exec client tcpdump -i any -w /captures/modbus.pcap -s 0 port 502
```

This writes the packet capture to the mounted `captures/` directory.

## Example output

The client reads temperature and pressure values from the PLC and prints output similar to:

```text
Connected to simulated PLC at plc:502
Read 1: temperature=23.5, pressure=101.3
Read 2: temperature=23.5, pressure=101.3
...
```

## Notes

- The PLC is intentionally simple and meant for lab/testing scenarios.
- This is not production-grade industrial control software.
- The simulation is focused on Modbus TCP behavior and packet capture analysis.
