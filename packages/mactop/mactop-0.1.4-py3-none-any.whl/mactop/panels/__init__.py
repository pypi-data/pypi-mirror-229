from mactop.panels.battery import BatteryPanel
from mactop.panels.sensors import SensorsPanel
from mactop.panels.tasks import TaskTable
from mactop.panels.energy import EnergyPanel
from mactop.panels.cpu_total_usage_bar import CPUTotalUsageBarPanel
from mactop.panels.cpu_percpu_usage import CPUUsageBarPanel
from mactop.panels.cpu_total_usage_text import CPUTotalUsageTextPanel
from mactop.panels.network_iobyte_rate_text import NetworkIOByteRateText
from mactop.panels.network_iopacket_rate_text import NetworkIOPacketRateText
from mactop.panels.swap_memory import SwapMemoryInOutText, SwapMemoryUsageVBar
from mactop.panels.virtual_memory import MemoryStatsText, MemoryUsageVBar
from mactop.panels.network_sparkline import (
    NetworkIByteRateSparkline,
    NetworkOByteRateSparkline,
    NetworkIPacketRateSparkline,
    NetworkOPacketRateSparkline,
)

from mactop.panels.disk import (
    DiskIOOpsPerSText,
    DiskIOBytesPerSText,
    DiskROpsPerSSparkline,
    DiskWOpsPerSSparkline,
    DiskRBytesPerSSparkline,
    DiskWBytesPerSSparkline,
)
from mactop.panels.loadavg import LoadAvgText
from mactop.panels.uptime import UptimeText
from mactop.panels.cpu_freq import CPUFreqPanel

PANELS = {
    "SensorsPanel": SensorsPanel,
    "BatteryPanel": BatteryPanel,
    "TaskTable": TaskTable,
    "EnergyPanel": EnergyPanel,
    "CPUTotalUsageBarPanel": CPUTotalUsageBarPanel,
    "CPUTotalUsageTextPanel": CPUTotalUsageTextPanel,
    "CPUUsageBarPanel": CPUUsageBarPanel,
    "NetworkIOByteRateText": NetworkIOByteRateText,
    "NetworkIByteRateSparkline": NetworkIByteRateSparkline,
    "NetworkOByteRateSparkline": NetworkOByteRateSparkline,
    "NetworkIPacketRateSparkline": NetworkIPacketRateSparkline,
    "NetworkOPacketRateSparkline": NetworkOPacketRateSparkline,
    "NetworkIOPacketRateText": NetworkIOPacketRateText,
    "SwapMemoryInOutText": SwapMemoryInOutText,
    "SwapMemoryUsageVBar": SwapMemoryUsageVBar,
    "MemoryStatsText": MemoryStatsText,
    "MemoryUsageVBar": MemoryUsageVBar,
    "DiskIOOpsPerSText": DiskIOOpsPerSText,
    "DiskIOBytesPerSText": DiskIOBytesPerSText,
    "DiskROpsPerSSparkline": DiskROpsPerSSparkline,
    "DiskWOpsPerSSparkline": DiskWOpsPerSSparkline,
    "DiskRBytesPerSSparkline": DiskRBytesPerSSparkline,
    "DiskWBytesPerSSparkline": DiskWBytesPerSSparkline,
    "LoadAvgText": LoadAvgText,
    "UptimeText": UptimeText,
    "CPUFreqPanel": CPUFreqPanel,
}
