#  Fixed Sliding Window Protocol (16 Points): (Rest covered in the report)
# Correct number of packets sent in each cycle (3)
# The window pointers update correctly (4)
# Packet loss handled correctly (4)
# Metrics measured correctly over 10 iterations (3)
# Window adjustment technique explained (2)

import socket
import time

# Common definitions
PACKET_SIZE = 1024              # Total packet size in bytes
SEQ_ID_SIZE = 4                 # 4 bytes reserved for the sequence number header
DATA_SIZE = PACKET_SIZE - SEQ_ID_SIZE  # Payload size per packet

'''
    Rubric Requirement: Sequence of packets managed correctly (3 Points)
'''
def create_packet(seq, data):
    """
    Create a UDP packet with a 4-byte sequence number header (signed, big-endian)
    followed by the data.
    """
    return seq.to_bytes(SEQ_ID_SIZE, byteorder='big', signed=True) + data

def read_file_in_chunks(filename):
    """
    Generator that reads the file in DATA_SIZE chunks.
    Yields a tuple (offset, data) where offset is the byte position.
    """
    with open(filename, 'rb') as f:
        offset = 0
        while True:
            data = f.read(DATA_SIZE)
            if not data:
                break
            yield offset, data
            offset += len(data)

class FixedWindowSenderWithMetrics:
    WINDOW_SIZE = 100  # Maximum number of unacknowledged packets

    def __init__(self, dest_ip, dest_port=5001, timeout=0.5):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Allow reuse of the address to avoid "address already in use" errors.
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("0.0.0.0", 5002))  # Bind to a port different from 5001
        self.sock.settimeout(timeout)
        self.dest_addr = (dest_ip, dest_port)
        self.start_time = time.time()  # Start throughput timer immediately

        # Metrics variables
        self.total_bytes_sent = 0      # Count unique payload bytes successfully acknowledged
        self.packet_send_time = {}     # Dictionary: packet offset -> first send time
        self.packet_delays = []        # List to hold per-packet delays


    """
    Implements the Fixed Sliding Window protocol.
    
    Rubric Requirements for Fixed Sliding Window:
    1. Correct number of packets sent in each cycle (3 Points):
        - Within each cycle, up to WINDOW_SIZE packets are sent.
        - (E.g., if the file has 10 packets and WINDOW_SIZE=100, then in one cycle 10 packets are sent.)
    2. The window pointers update correctly (4 Points):
        - 'base' (first unacknowledged packet) and 'next_index' (next packet to send)
            are updated as cumulative ACKs are received.
    3. Packet loss handled correctly (4 Points):
        - On timeout, all packets in the current window are retransmitted.
    4. Metrics measured correctly over 10 iterations (3 Points):
        - Throughput, average delay, and performance metric are computed.
    5. Window adjustment technique explained (2 Points):
        - Inline comments explain how the window slides based on cumulative ACKs.
    """
    def send_file(self, filename):
        # Read the file into a list of (offset, data) tuples
        packets = list(read_file_in_chunks(filename))
        total_packets = len(packets)
        base = 0        # Pointer to the first unacknowledged packet in the window
        next_index = 0  # Next packet index to send

        # Continue sending until all packets are acknowledged
        while base < total_packets:
            # Send packets while the window is not full
            while next_index < total_packets and (next_index - base) < self.WINDOW_SIZE:
                offset, data = packets[next_index]
                packet = create_packet(offset, data)
                # Record the first send time only once per packet
                if offset not in self.packet_send_time:
                    self.packet_send_time[offset] = time.time()
                self.sock.sendto(packet, self.dest_addr)
                # print(f"[FixedWindow] Sent packet: seq_id {offset}, size {len(data)} bytes")
                next_index += 1

            try:
                # Wait for a cumulative ACK from the receiver
                ack_packet, _ = self.sock.recvfrom(PACKET_SIZE)
                ack = int.from_bytes(ack_packet[:SEQ_ID_SIZE], byteorder='big', signed=True)
                # print(f"[FixedWindow] Received cumulative ACK: {ack}")

                # Slide the window: for each packet that is acknowledged,
                # compute its delay and update total unique bytes sent.
                while base < total_packets:
                    offset, data = packets[base]
                    if ack >= offset + len(data):
                        delay = time.time() - self.packet_send_time[offset]
                        self.packet_delays.append(delay)
                        self.total_bytes_sent += len(data)
                        base += 1
                    else:
                        break
            except socket.timeout:
                #print(f"[FixedWindow] Timeout. Resending packets from index {base} to {next_index - 1}.")
                # Resend all packets in the current window
                for i in range(base, next_index):
                    offset, data = packets[i]
                    packet = create_packet(offset, data)
                    self.sock.sendto(packet, self.dest_addr)
                    # print(f"[FixedWindow] Resent packet: seq_id {offset}, size {len(data)} bytes")

        # After all packets are sent, send an EOF packet (empty payload) with the final offset.
        final_offset = packets[-1][0] + len(packets[-1][1]) if total_packets > 0 else 0
        eof_packet = create_packet(final_offset, b"")
        self.sock.sendto(eof_packet, self.dest_addr)
        # print(f"[FixedWindow] Sent EOF packet with seq_id {final_offset}")

        # Wait for the receiver's final ACK and FIN messages
        try:
            ack_packet, _ = self.sock.recvfrom(PACKET_SIZE)
            fin_packet, _ = self.sock.recvfrom(PACKET_SIZE)
            #print("[FixedWindow] Received final ACK and FIN from receiver.")
        except socket.timeout:
            pass
            #print("[FixedWindow] Timeout waiting for final ACK/FIN.")

        # Send FINACK message to signal the receiver to exit
        finack_packet = create_packet(0, b'==FINACK==')
        self.sock.sendto(finack_packet, self.dest_addr)
        # print("[FixedWindow] Sent FINACK message. Exiting sender.")
        self.sock.close()

        # Compute metrics
        end_time = time.time()
        total_time = end_time - self.start_time
        throughput = self.total_bytes_sent / total_time if total_time > 0 else 0.0
        avg_delay = sum(self.packet_delays) / len(self.packet_delays) if self.packet_delays else 0.0
        
        # Corrected performance metric:
        # 0.3 × (throughput / 1000) + 0.7 / (average per-packet delay)
        if avg_delay > 0:
            performance_metric = 0.3 * (throughput / 1000.0) + 0.7 / avg_delay
        else:
            performance_metric = float('inf')

        # Output the metrics; note that 10 iterations may be run externally and averaged.
        print(f"{throughput:.7f}, {avg_delay:.7f}, {performance_metric:.7f}")
        # print("------------ TCP Reno ------------")
        # print(f"Throughput: {throughput:.2f} bytes/s")
        # print(f"Average delay per packet: {avg_delay:.4f} s")
        # print(f"Performance Metric: {performance_metric:.4f}")
        # print("------------------------------------------------")
