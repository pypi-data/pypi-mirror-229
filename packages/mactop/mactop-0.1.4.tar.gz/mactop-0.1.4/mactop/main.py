import os
import logging
from pathlib import Path

import click
from textual.app import App, ComposeResult
from textual.widgets import Footer

from mactop.metrics_source import PowerMetricsManager, IORegManager, PsutilManager
from mactop.widgets.header import MactopHeader
from mactop.layout_loader import XmlLayoutLoader
from . import __version__


LOG_LOCATION = "/tmp/mactop.log"
logger = logging.getLogger(__name__)


def setup_log(enabled=True, loglocation=LOG_LOCATION):
    if enabled:
        logging.basicConfig(
            filename=os.path.expanduser(loglocation),
            filemode="a",
            format="%(asctime)s %(levelname)5s (%(module)s) %(message)s",
            level="DEBUG",
        )
    else:
        logging.disable(logging.CRITICAL)
    logger.info("------ mactop ------")


class MactopApp(App):
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]
    BINDINGS = [("q", "exit", "Exit")]

    def __init__(self, app_body_items, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app_body_items = app_body_items

    def on_mount(self) -> None:
        self.title = "mactop"
        self.sub_title = f"v{__version__}"

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield MactopHeader(show_clock=True)
        yield Footer()

        for item in self.app_body_items:
            yield item

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    def action_exit(self) -> None:
        self.exit()


@click.command()
@click.option(
    "--theme",
    "-t",
    default=(Path(__file__).parent / "mactop.xml"),
    help="Mactop theme file location.",
)
@click.option(
    "--refresh-interval",
    "-r",
    default=1.0,
    help="Refresh interval seconds",
)
def main(theme, refresh_interval):
    setup_log()

    metrics_source_manager = PowerMetricsManager(refresh_interval)
    metrics_source_manager.start()

    ioreg_manager = IORegManager(refresh_interval)
    ioreg_manager.start()

    psutil_manager = PsutilManager(refresh_interval)
    psutil_manager.start()

    layout_loader = XmlLayoutLoader(theme, refresh_interval)
    app_body_items, styles_content = layout_loader.load()
    MactopApp.CSS = styles_content
    app = MactopApp(app_body_items)
    app.run()

    logger.info("Mactop exited")
    metrics_source_manager.stop()
    ioreg_manager.stop()
    logger.info("Metrics stopped")
