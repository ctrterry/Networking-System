#!/usr/bin/env python3
import sys
from stopAndWait import StopAndWaitSenderWithMetrics
from fixedSlidingWindow import FixedWindowSenderWithMetrics
from tcpReno import TcpRenoSenderWithMetrics

def main():
    if len(sys.argv) < 4:
        print("Usage: python sender.py <protocol> <filename> <dest_ip>")
        print("  protocol options: stopAndWait, fixedSlidingWindow, tcpReno")
        sys.exit(1)
    
    protocol_choice = sys.argv[1].lower()
    filename = sys.argv[2]
    dest_ip = sys.argv[3]
    
    if protocol_choice == "stopandwait":
        sender = StopAndWaitSenderWithMetrics(dest_ip, dest_port=5001)
    elif protocol_choice == "fixedslidingwindow":
        sender = FixedWindowSenderWithMetrics(dest_ip, dest_port=5001)
    elif protocol_choice == "tcpreno":
        sender = TcpRenoSenderWithMetrics(dest_ip, dest_port=5001)
    else:
        print("Unknown protocol. Choose 'stopAndWait', 'fixedSlidingWindow', or 'tcpReno'.")
        sys.exit(1)
    
    sender.send_file(filename)

if __name__ == "__main__":
    main()
