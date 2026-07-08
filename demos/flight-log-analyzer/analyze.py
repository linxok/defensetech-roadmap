import argparse
import matplotlib.pyplot as plt
from pyulog import ULog

parser = argparse.ArgumentParser()
parser.add_argument('--log', required=True)
parser.add_argument('--output', default='report.png')
args = parser.parse_args()

log = ULog(args.log)
print('Topics:')
for d in log.data_list:
    print(f' - {d.name}')

# Example: plot altitude from vehicle_global_position if available
alt_data = None
for d in log.data_list:
    if d.name == 'vehicle_global_position':
        alt_data = d
        break

if alt_data is not None:
    t = alt_data.data['timestamp'] / 1e6
    alt = alt_data.data['alt']
    plt.figure(figsize=(10, 5))
    plt.plot(t, alt)
    plt.xlabel('Time (s)')
    plt.ylabel('Altitude (m)')
    plt.title('Flight Altitude')
    plt.grid(True)
    plt.savefig(args.output)
    print(f'Saved plot to {args.output}')
else:
    print('vehicle_global_position topic not found')
