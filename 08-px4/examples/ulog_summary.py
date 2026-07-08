from pyulog import ULog

log = ULog('log.ulg')
print("Topics:")
for d in log.data_list:
    print(f" - {d.name}")
