
import socket
import struct
import time

HOST = "0.0.0.0"
PORT = 502

# Simulated sensor registers:
# Register 0: temperature x 10
# Register 1: pressure x 10
REGISTERS = [235, 1013]


def handle_client(conn, address):
    print(f"Client connected: {address}")

    with conn:
        while True:
            # Modbus TCP read request: 12 bytes for function 3.
            request = b""
            while len(request) < 12:
                chunk = conn.recv(12 - len(request))
                if not chunk:
                    return
                request += chunk

            tid, protocol, length, unit = struct.unpack(
                ">HHHB", request[:7]
            )
            function = request[7]

            if protocol != 0 or function != 3:
                print("Unsupported request received")
                continue

            start, quantity = struct.unpack(">HH", request[8:12])

            if quantity < 1 or quantity > 10:
                pdu = struct.pack(">BB", function | 0x80, 3)
            elif start + quantity > len(REGISTERS):
                pdu = struct.pack(">BB", function | 0x80, 2)
            else:
                values = REGISTERS[start:start + quantity]
                data = b"".join(struct.pack(">H", v) for v in values)
                pdu = struct.pack(">BB", function, len(data)) + data

            # MBAP length counts the unit ID plus PDU bytes.
            response = struct.pack(
                ">HHHB", tid, 0, len(pdu) + 1, unit
            ) + pdu

            conn.sendall(response)
            print(
                f"{time.strftime('%H:%M:%S')} "
                f"Read request start={start} quantity={quantity}"
            )


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen()
        print(f"Simulated PLC listening on {HOST}:{PORT}")

        while True:
            conn, address = server.accept()
            try:
                handle_client(conn, address)
            except (ConnectionError, OSError) as exc:
                print(f"Client connection ended: {exc}")


if __name__ == "__main__":
    main()