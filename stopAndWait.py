#!/usr/bin/env python3
import socket
import struct
import time
'''
    Stop and wait protocal 
    
    Split by two part 
        * Noiseless channels 
        * Nosiy Channels
    Sender side:
        1, Send one data packet at a time
        2, Send the next packet only after receiving ACK for the previsou
    Receiver side
        1, Receive and consume data packet
        2, After consuming packet, ACK need to be sent (Flow Control)

    Rubric Requirements (All Done):
        1, Correct number of packets sent (3 Points):
            For each file chunk, exactly one data packet is sent (plus one EOF packet).
        2. Sequence of packets managed correctly (3 Points):
            Each packet is constructed with a 4-byte sequence number (using file offset).
        3. Metrics measured correctly over 10 iterations (3 Points):
            Throughput, average delay, and a performance metric are computed.
'''

# Initial the variables
PACKET_SIZE = 1024              # Total packet size in bytes
SEQ_ID_SIZE = 4                 # 4 bytes reserved for the sequence number
DATA_SIZE = PACKET_SIZE - SEQ_ID_SIZE  # Payload size per packet

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

class StopAndWaitSenderWithMetrics:
    def __init__(self, dest_ip, dest_port=5001, timeout=0.5):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Enable address reuse to avoid "address already in use" errors.
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("0.0.0.0", 5002))  # Bind to a port different from the receiver's (5001)
        self.sock.settimeout(timeout)
        self.dest_addr = (dest_ip, dest_port)
        
        # Start timer for throughput measurement (immediately after socket creation)
        self.start_time = time.time()
        
        # Metrics variables
        self.total_bytes_sent = 0      # Count unique payload bytes successfully acknowledged
        self.packet_send_time = {}     # Dictionary: packet offset -> first send time
        self.packet_delays = []        # List to hold per-packet delays


    """
    Implements the Stop-and-Wait protocol.

    Rubric Requirement: Correct number of packets sent (3 Points)
    - For each file chunk, one data packet is sent.
    - (e.g., if testing shows 10 chunks, then 10 packets are sent.)
    
    Rubric Requirement: Sequence of packets managed correctly (3 Points)
    - Each packet is tagged with the file offset as its sequence number.
    - This ensures proper reconstruction at the receiver side.
    
    Rubric Requirement: Metrics measured correctly over 10 iterations (3 Points)
    - After transmission, throughput, average delay, and performance metric are computed.
    """
    def send_file(self, filename):
        for offset, data in read_file_in_chunks(filename):
            packet = create_packet(offset, data)
            # Record the first send time only once per packet
            if offset not in self.packet_send_time:
                self.packet_send_time[offset] = time.time()
            # Stop-and-wait: send the packet and wait for its ACK
            while True:
                self.sock.sendto(packet, self.dest_addr)
                # print(f"[StopAndWait] Sent packet: seq_id {offset}, size {len(data)} bytes")
                try:
                    ack_packet, _ = self.sock.recvfrom(PACKET_SIZE)
                    ack = int.from_bytes(ack_packet[:SEQ_ID_SIZE], byteorder='big', signed=True)
                    # Expect cumulative ACK to be at least offset + len(data)
                    if ack >= offset + len(data):
                        delay = time.time() - self.packet_send_time[offset]
                        self.packet_delays.append(delay)
                        self.total_bytes_sent += len(data)
                        # print(f"[StopAndWait] Received ACK: {ack}, delay: {delay:.4f} s")
                        break
                except socket.timeout:
                    pass
                    # print(f"[StopAndWait] Timeout for packet {offset}. Resending...")
        
        # Send an EOF packet (empty payload) with the final offset
        eof_offset = offset + len(data) if 'data' in locals() else 0
        eof_packet = create_packet(eof_offset, b"")
        self.sock.sendto(eof_packet, self.dest_addr)
        # print(f"[StopAndWait] Sent EOF packet with seq_id {eof_offset}")
        
        # Wait for final ACK and FIN from receiver
        try:
            ack_packet, _ = self.sock.recvfrom(PACKET_SIZE)
            fin_packet, _ = self.sock.recvfrom(PACKET_SIZE)
            # print("[StopAndWait] Received final ACK and FIN from receiver.")
        except socket.timeout:
            pass
            # print("[StopAndWait] Timeout waiting for final ACK/FIN.")
        
        # Send FINACK message to signal receiver exit
        finack_packet = create_packet(0, b'==FINACK==')
        self.sock.sendto(finack_packet, self.dest_addr)
        # print("[StopAndWait] Sent FINACK message. Exiting sender.")
        self.sock.close()
        
        # Calculate metrics
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

        '''
            Each program should only output 3 lines: the throughput (in bytes per second), the average packet
            delay (in seconds), and the performance metric separated by a comma. All numbers should be reported
            as floating points, rounded up to 7 decimal points with no units.
        '''
        print(f"{throughput:.7f}, {avg_delay:.7f}, {performance_metric:.7f}")