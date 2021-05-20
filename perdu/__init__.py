import os
import webbrowser

import click
import requests

from .__version__ import __version__
from .app import create_app

__all__ = ["app", "web"]

here = os.path.abspath(os.path.dirname(__file__))

app = create_app()


@click.command("start", short_help="init / start")
@click.argument("arg", type=str)
def start(arg):
    if arg == "start":
        # lsof -i:9200
        # kill -9 <PID>
        webbrowser.open(os.path.join("file://" + here, "web/perdu.html"))
        app.run()

    elif arg == "scan":
        print("Indexing every python files.")
        r = requests.get("http://localhost:5000/init/")
        print(r.json())
