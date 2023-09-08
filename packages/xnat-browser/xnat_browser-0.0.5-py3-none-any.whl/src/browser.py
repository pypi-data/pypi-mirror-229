import logging

import xnat
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import ScrollableContainer, HorizontalScroll
from textual.widgets import Header, Footer, Label, RichLog
from xnat.exceptions import (XNATAuthError, XNATLoginFailedError, XNATExpiredCredentialsError,
                             XNATNotConnectedError)

from src.log_handler import TextualLogHandler
from src.quit_screen import QuitScreen
from src.xnat_tree import XnatTree


class XnatBrowser(App):
    CSS_PATH = 'browser.tcss'
    BINDINGS = [
        Binding('ctrl+t', 'toggle_dark', show=False),
        Binding('q', 'quit', 'Quit'),
        Binding('escape', 'dismiss', show=False),
    ]

    def __init__(self, server: str, log_level: int = logging.INFO) -> None:
        super().__init__()
        self._server = server
        self.logger = logging.getLogger('xnat_browser')
        self.logger.setLevel(log_level)

        try:
            self.session = xnat.connect(server=self._server, default_timeout=300)
        except (XNATAuthError, XNATLoginFailedError, XNATExpiredCredentialsError, XNATNotConnectedError) as e:
            self.logger.error('Error connecting to XNAT server.')
            self.logger.debug(e)

    def _setup_logging(self) -> RichLog:
        log_window = RichLog(id='rich_log', name='Log')

        log_handler = TextualLogHandler(log_window)
        log_handler.setFormatter(
            logging.Formatter('%(asctime)s %(levelname)7s [%(filename)15s:%(lineno)3s - %(funcName)20s()] %(message)s'))

        self.logger.addHandler(log_handler)

        return log_window

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with HorizontalScroll(id='h_scroll'):
            output = Label(id='dicom_info', expand=True)
            yield XnatTree(self._server, output, self.logger, id='xnat_tree')
            with ScrollableContainer(id='dicom_info_container'):
                yield output
        yield self._setup_logging()
        yield Footer()

    def action_dismiss(self) -> None:
        self.query_one("#dicom_info", Label).update('')

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark

    async def action_quit(self) -> None:
        await self.push_screen(QuitScreen())
