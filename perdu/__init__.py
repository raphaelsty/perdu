import os
import time
import webbrowser

import click
import requests
from elasticsearch import Elasticsearch
from rich import print

from .__version__ import __version__
from .app import create_app

__all__ = ["app", "web"]

here = os.path.abspath(os.path.dirname(__file__))


@click.command("start", short_help="init / start")
@click.argument("arg", type=str)
def start(arg):
    if arg == "start":
        # lsof -i:9200
        # lsof -i:5000
        # kill -9 <PID>

        os.popen("elasticsearch")
        es = Elasticsearch()

        while not es.ping():
            print("🟠 Waiting for ElasticSearch, it should start soon.")
            time.sleep(1)

        print("🟢 ElasticSearch is ready to go.")
        app = create_app(es=es)

        print("🎉 Starting the app.")
        webbrowser.open(os.path.join("file://" + here, "web/perdu.html"))
        app.run()

    elif arg == "scan":
        print("🤖 Indexing every python files and notebooks.")
        r = requests.get("http://localhost:5000/init/")
        print(r.json())

    elif arg == "open":
        print("😎 Opening web.")
        webbrowser.open(os.path.join("file://" + here, "web/perdu.html"))
