import os
import webbrowser

import click
from rich import print

from .app import create_app, init_pipeline

__all__ = ["app", "web"]

here = os.path.abspath(os.path.dirname(__file__))


@click.command("start", short_help="init / start")
@click.argument("arg", type=str)
@click.option("-p", default="./", help="Path to index.")
def start(arg, p):

    if arg == "start":
        # lsof -i:9200
        # lsof -i:5000
        # kill -9 <PID>

        app = create_app(here=here)

        print("🎉 Starting the app.")
        webbrowser.open(os.path.join("file://" + here, "web/perdu.html"))
        app.run()

    elif arg == "scan":
        print("🤖 Indexing every python files and notebooks.")
        init_pipeline(p=p, here=here)

    elif arg == "open":
        print("😎 Opening web.")
        webbrowser.open(os.path.join("file://" + here, "web/perdu.html"))
