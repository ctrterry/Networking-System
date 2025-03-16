import numpy as np
import matplotlib.pyplot as plt

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

protocols = ['Stop-and-Wait', 'Fixed Sliding Window', 'TCP Reno']
metrics_labels = ['Throughput (bytes/s)', 'Average Packet Delay (s)', 'Performance Metric']

# Compute mean and standard deviation for each metric in each protocol
def compute_stats(data):
    avg = np.mean(data, axis=0)
    std = np.std(data, axis=0, ddof=1)  # Sample standard deviation
    return avg, std

avg_SW, std_SW = compute_stats(data_StopAndWait)
avg_FS, std_FS = compute_stats(data_FixSlidingWindow)
avg_TR, std_TR = compute_stats(data_TCPReno)

# Stack the averages and stds into arrays (each row corresponds to one protocol)
avg_all = np.array([avg_SW, avg_FS, avg_TR])
std_all = np.array([std_SW, std_FS, std_TR])

# Create bar charts with error bars for each metric
fig, axs = plt.subplots(1, 3, figsize=(18, 6))

for i in range(3):
    axs[i].bar(protocols, avg_all[:, i], yerr=std_all[:, i], capsize=5, color=['skyblue', 'salmon', 'lightgreen'])
    axs[i].set_title(metrics_labels[i])
    axs[i].set_ylabel(metrics_labels[i])
    axs[i].grid(True)

plt.suptitle("Protocol Performance Comparison (10 Trials)", fontsize=18)
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.show()
