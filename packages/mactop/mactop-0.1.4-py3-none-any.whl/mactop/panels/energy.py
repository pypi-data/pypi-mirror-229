import logging


from textual.app import ComposeResult

from mactop.metrics_store import metrics
from mactop.widgets import LabeledSparkline
from ._base import BaseStatic

logger = logging.getLogger(__name__)


class EnergyPanel(BaseStatic):
    BORDER_TITLE = "Energy"

    DEFAULT_CSS = """
    EnergyPanel {
        border: solid $secondary;
        border-title-align: left;
    }
    """

    def compose(self) -> ComposeResult:
        yield LabeledSparkline(
            update_fn=lambda: metrics.get_powermetrics().processor_intel.package_watts_history,
            value_render_fn=lambda v: f" {v:.1f} W",
            update_interval=self.refresh_interval,
            prefix_label="CPU Power",
        )
