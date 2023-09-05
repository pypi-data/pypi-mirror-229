
import arrow
from decimal import Decimal
from datetime import timedelta

from tendril.utils.types.time import Frequency
from tendril.utils.types.time import TimeSpan
from tendril.utils.types.memory import MemorySize
from tendril.utils.types.thermodynamic import Temperature

from tendril.monitors.spec import MonitorSpec
from tendril.monitors.spec import MonitorExportLevel
from tendril.monitors.spec import MonitorPublishFrequency
from tendril.monitors.spec import ensure_str

from tendril.core.tsdb.constants import TimeSeriesFundamentalType


sxm_media_monitors_spec = [
    MonitorSpec('play_success', default=0,
                localization_from_hierarchy=False,
                flatten_cardinality=('device', 'filename'),
                structure='duration', deserializer=timedelta,
                serializer=lambda x: x.total_seconds(),
                publish_frequency=MonitorPublishFrequency.ALWAYS,
                export_level=MonitorExportLevel.NEVER,
                is_cumulative=True,
                is_continuous=False),
]
