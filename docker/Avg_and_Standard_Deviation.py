# Reference Standard Deviation: https://www.geeksforgeeks.org/numpy-std-in-python/

import numpy as np

# Data for Stop-and-Wait Protocol
data_StopAndWait = np.array([
    [1111953.4812432, 0.0005690, 1563.8664629],
    [873983.4577880, 0.0007512, 1194.0009790],
    [1270649.2156067, 0.0005077, 1759.9693876],
    [1477528.5377671, 0.0004438, 2020.5129612],
    [1472593.1973721, 0.0004455, 2012.9903616],
    [1492192.7988637, 0.0004410, 2034.8169519],
    [1487224.1927762, 0.0004439, 2023.1356428],
    [1483593.4103565, 0.0004425, 2026.9496081],
    [1478461.9526122, 0.0004443, 2019.1264320],
    [1490003.7375403, 0.0004372, 2048.0965886]
])

# Data for Fixed Sliding Window Protocol (size 100 packets)
data_FixSlidingWindow = np.array([
    [755896.2049663, 0.1120487, 233.0161436],
    [608845.0149962, 0.1432475, 187.5401526],
    [568961.3425169, 0.1545316, 175.2182203],
    [532102.6712431, 0.1506968, 164.2758914],
    [560150.6762762, 0.1574987, 172.4896830],
    [472329.6901617, 0.1864596, 145.4530717],
    [559332.6743398, 0.1623949, 172.1102834],
    [468842.1949193, 0.1932368, 144.2751570],
    [529710.3388190, 0.1637640, 163.1875447],
    [690044.5894679, 0.1200976, 212.8419684]
])

# Data for TCP Reno Protocol
data_TCPReno = np.array([
    [1441459.7101365, 0.0457288, 447.7455487],
    [1015089.2405779, 0.0529494, 317.7469364],
    [1033538.7462529, 0.0622261, 321.3109194],
    [1303222.3337947, 0.0357249, 410.5608963],
    [933345.2088931, 0.0654312, 290.7018283],
    [1020165.4377236, 0.0728123, 315.6633892],
    [1468842.6117607, 0.0283602, 465.3352816],
    [1734871.2301375, 0.0244257, 549.1197238],
    [1762177.7840367, 0.0278623, 553.7768472],
    [1244108.5265520, 0.0408151, 390.3830686]
])

# Function to compute average and standard deviation
def compute_statistics(data, protocol_name):
    avg = np.mean(data, axis=0)
    std_dev = np.std(data, axis=0, ddof=1)  # ddof=1 for sample standard deviation
    print(f"========= {protocol_name} =========")
    print(f"Average Throughput (bytes/s): {avg[0]:.2f}")
    print(f"Standard Deviation Throughput: {std_dev[0]:.2f}")
    print(f"Average Packet Delay (s): {avg[1]:.8f}")
    print(f"Standard Deviation Packet Delay: {std_dev[1]:.8f}")
    print(f"Average Metric Performance: {avg[2]:.2f}")
    print(f"Standard Deviation Metric Performance: {std_dev[2]:.2f}")
    print("=====================================\n")

# Compute and print statistics for each protocol
compute_statistics(data_StopAndWait, "Stop-and-Wait Protocol")
compute_statistics(data_FixSlidingWindow, "Fixed Sliding Window (100 packets)")
compute_statistics(data_TCPReno, "TCP Reno")

