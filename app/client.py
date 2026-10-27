
import socket
import struct
import time

PLC_HOST = "plc"
PLC_PORT = 502


def read_registers(sock, transaction_id, start, quantity):
    # MBAP header: transaction ID, protocol ID, length, unit ID.
    header = struct.pack(
        ">HHHBBHH",
        transaction_id, 0, 6, 1, 3, start, quantity
    )
    sock.sendall(header)

    # Read the 7-byte MBAP header first.
    response_header = b""
    while len(response_header) < 7:
        chunk = sock.recv(7 - len(response_header))
        if not chunk:
            raise ConnectionError("PLC closed the connection")
        response_header += chunk

    tid, protocol, length, unit = struct.unpack(
        ">HHHB", response_header
    )

    # Length includes the unit ID, already read, plus the PDU.
    remaining = length - 1
    pdu = b""
    while len(pdu) < remaining:
        chunk = sock.recv(remaining - len(pdu))
        if not chunk:
            raise ConnectionError("Incomplete Modbus response")
        pdu += chunk

    if tid != transaction_id or protocol != 0:
        raise ValueError("Unexpected Modbus response header")

    if pdu[0] & 0x80:
        raise ValueError(f"Modbus exception code: {pdu[1]}")

    if pdu[0] != 3:
        raise ValueError(f"Unexpected function code: {pdu[0]}")

    byte_count = pdu[1]
    data = pdu[2:]

    if len(data) != byte_count or byte_count != quantity * 2:
        raise ValueError("Unexpected register response size")

    return list(struct.unpack(">" + "H" * quantity, data))


def main():
    with socket.create_connection((PLC_HOST, PLC_PORT), timeout=5) as sock:
        print(f"Connected to simulated PLC at {PLC_HOST}:{PLC_PORT}")

        for tid in range(1, 11):
            values = read_registers(sock, tid, 0, 2)
            temperature = values[0] / 10
            pressure = values[1] / 10

            print(
                f"Read {tid}: temperature={temperature:.1f}, "
                f"pressure={pressure:.1f}"
            )
            time.sleep(2)


if __name__ == "__main__":
    main()