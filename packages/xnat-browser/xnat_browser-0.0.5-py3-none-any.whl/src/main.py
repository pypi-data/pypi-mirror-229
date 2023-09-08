""" CLI """
import logging

import typer
import rich.traceback
import rich.logging

from src.browser import XnatBrowser


app = typer.Typer(add_completion=False, no_args_is_help=True)


@app.command()
def browser(server: str, verbose: bool = typer.Option(False, '--verbose', '-v')) -> None:
    XnatBrowser(server, logging.DEBUG if verbose else logging.INFO).run()


if __name__ == "__main__":
    rich.traceback.install(width=None, word_wrap=True)
    app()
