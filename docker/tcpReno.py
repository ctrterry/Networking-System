import socket
import time

PACKET_SIZE = 1024
SEQ_ID_SIZE = 4
DATA_SIZE = PACKET_SIZE - SEQ_ID_SIZE

def create_packet(seq, data):
    return seq.to_bytes(SEQ_ID_SIZE, byteorder='big', signed=True) + data

def read_file_in_chunks(filename):
    with open(filename, 'rb') as f:
        offset = 0
        while True:
            data = f.read(DATA_SIZE)
            if not data:
                break
            yield offset, data
            offset += len(data)

class TcpRenoSenderWithMetrics:
    def __init__(self, dest_ip, dest_port=5001, timeout=0.5):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("0.0.0.0", 5002))
        self.sock.settimeout(timeout)
        self.dest_addr = (dest_ip, dest_port)
        self.start_time = time.time()
        self.total_bytes_sent = 0
        self.packet_send_time = {}  # Records send times by packet offset
        self.packet_delays = []     # List of computed delays
        # TCP Reno parameters:
        self.cwnd = 1          # Congestion window (in packets)
        self.ssthresh = 64     # Slow-start threshold (in packets)
        self.last_ack = -1
        self.dup_ack_count = 0

    def send_file(self, filename):
        packets = list(read_file_in_chunks(filename))
        total_packets = len(packets)
        base = 0
        next_index = 0

        while base < total_packets:
            # Send new packets while within the current congestion window.
            while next_index < total_packets and (next_index - base) < self.cwnd:
                offset, data = packets[next_index]
                # Always update the send time for accurate delay measurement.
                self.packet_send_time[offset] = time.time()
                packet = create_packet(offset, data)
                self.sock.sendto(packet, self.dest_addr)
                next_index += 1

            try:
                ack_packet, _ = self.sock.recvfrom(PACKET_SIZE)
                ack = int.from_bytes(ack_packet[:SEQ_ID_SIZE], byteorder='big', signed=True)
                if ack > self.last_ack:
                    self.dup_ack_count = 0
                    self.last_ack = ack
                    # Slide the window and record delays for all acknowledged packets.
                    while base < total_packets:
                        offset, data = packets[base]
                        # If ACK acknowledges this packet
                        if ack >= offset + len(data):
                            # Safeguard: if the send time is missing, record it now.
                            if offset not in self.packet_send_time:
                                self.packet_send_time[offset] = time.time()
                            delay = time.time() - self.packet_send_time[offset]
                            self.packet_delays.append(delay)
                            self.total_bytes_sent += len(data)
                            base += 1
                        else:
                            break
                    # Update congestion window: slow start (cwnd < ssthresh) then congestion avoidance.
                    if self.cwnd < self.ssthresh:
                        self.cwnd += 1
                    else:
                        self.cwnd += 1.0 / self.ssthresh
                else:
                    # Duplicate ACK received.
                    self.dup_ack_count += 1
                    if self.dup_ack_count == 3:
                        # Fast retransmit and recovery.
                        self.ssthresh = max(self.cwnd // 2, 1)
                        self.cwnd = self.ssthresh + 3
                        self.dup_ack_count = 0
                        offset, data = packets[base]
                        # Update send time unconditionally.
                        self.packet_send_time[offset] = time.time()
                        packet = create_packet(offset, data)
                        self.sock.sendto(packet, self.dest_addr)
            except socket.timeout:
                # Timeout occurred; assume packet loss and retransmit the packet at base.
                # print(f"[TCP Reno] Timeout occurred. Retransmitting packet at base index {base}.")
                self.ssthresh = max(self.cwnd // 2, 1)
                self.cwnd = 1
                offset, data = packets[base]
                # Update send time unconditionally.
                self.packet_send_time[offset] = time.time()
                packet = create_packet(offset, data)
                self.sock.sendto(packet, self.dest_addr)
                next_index = base  # Reset next_index to resend unACKed packets.

        # Send an EOF packet (empty payload) with the final sequence number.
        final_offset = packets[-1][0] + len(packets[-1][1]) if total_packets > 0 else 0
        eof_packet = create_packet(final_offset, b"")
        self.sock.sendto(eof_packet, self.dest_addr)

        try:
            # Wait for final ACK and FIN from receiver.
            ack_packet, _ = self.sock.recvfrom(PACKET_SIZE)
            fin_packet, _ = self.sock.recvfrom(PACKET_SIZE)
        except socket.timeout:
            pass
            # print("[TCP Reno] Timeout waiting for final ACK/FIN.")

        finack_packet = create_packet(0, b'==FINACK==')
        self.sock.sendto(finack_packet, self.dest_addr)
        self.sock.close()

        # Compute and print performance metrics.
        end_time = time.time()
        total_time = end_time - self.start_time
        throughput = self.total_bytes_sent / total_time if total_time > 0 else 0.0
        avg_delay = sum(self.packet_delays) / len(self.packet_delays) if self.packet_delays else 0.0
        if avg_delay > 0:
            performance_metric = 0.3 * (throughput / 1000.0) + 0.7 / avg_delay
        else:
            performance_metric = float('inf')

        '''
            Each program should only output 3 lines: the throughput (in bytes per second), the average packet
            delay (in seconds), and the performance metric separated by a comma. All numbers should be reported
            as floating points, rounded up to 7 decimal points with no units.
        '''
        # Output the metrics; note that 10 iterations may be run externally and averaged.
        print(f"{throughput:.7f}, {avg_delay:.7f}, {performance_metric:.7f}")
        # print("========== Metrics ==========")
        # print(f"Throughput: {throughput:.2f} bytes/s")
        # print(f"Average delay per packet: {avg_delay:.4f} s")
        # print(f"Performance Metric: {performance_metric:.4f}")
        # print("============================")