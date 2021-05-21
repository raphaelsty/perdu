import os
import re
import time

from elasticsearch import Elasticsearch, helpers
from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
from nbformat import NO_CONVERT, read

# export FLASK_APP=app.py
# export FLASK_ENV=development
# flask run

__all__ = [
    "create_app",
    "walk",
    "metadata_func",
    "metadata_notebook",
    "metadata_file",
    "scan_files",
]


def walk(path=os.environ["PERDU"], extension=".py"):
    files = []
    for d, _, f in os.walk(path):
        for file in f:
            if file.endswith(extension):
                files.append((os.path.join(d, file)))
    return files


def metadata_func(regex, file):
    """Read functions inside python files."""
    with open(file) as f:
        content = f.read()

    for func in regex.finditer(content):
        yield {
            "_index": "function",
            "_source": {
                "file": file,
                "date": time.ctime(os.path.getmtime(file)),
                "content": func.group(0),
            },
        }


def metadata_notebook(file):
    """Read code of notebooks."""
    with open(file) as fp:
        notebook = read(fp, NO_CONVERT)

    if "cells" in notebook:
        cells = [cell for cell in notebook["cells"] if cell["cell_type"] == "code"]
        for cell in cells:
            yield {
                "_index": "notebook",
                "_source": {
                    "file": file,
                    "date": time.ctime(os.path.getmtime(file)),
                    "content": cell["source"],
                },
            }


def metadata_full_notebook(file, id):
    """Read code of notebooks."""
    with open(file) as fp:
        notebook = read(fp, NO_CONVERT)

    if "cells" in notebook:
        cells = [cell for cell in notebook["cells"] if cell["cell_type"] == "code"]

        content = ""
        for cell in cells:
            content += "\n" + cell["source"]

        return {
            "_index": "full_notebook",
            "_id": id,
            "_source": {
                "file": file,
                "date": time.ctime(os.path.getmtime(file)),
                "content": content,
            },
        }


def metadata_file(file, id):
    """Read files and export complete file."""
    with open(file) as f:
        content = f.read()

    return {
        "_index": "classe",
        "_id": id,
        "_source": {
            "file": file,
            "date": time.ctime(os.path.getmtime(file)),
            "content": content,
        },
    }


def scan_files(es, list_files, list_notebooks):
    """Scan python files and notebooks and index them using ElasticSearch."""
    contents = []

    regex = re.compile(
        "((?:^[ \t]*)def \w+\(.*\): *(?=.*?[^ \t\n]).*\r?\n)"
        "|"
        "((^[ \t]*)def \w+\(.*\): *\r?\n"
        "(?:[ \t]*\r?\n)*"
        "\\3([ \t]+)[^ \t].*\r?\n"
        "(?:[ \t]*\r?\n)*"
        "(\\3\\4.*\r?\n(?: *\r?\n)*)*)",
        re.MULTILINE,
    )

    id = 0

    for id, file in enumerate(list_files):

        try:

            item = metadata_file(file, id)
            id += 1

            for item in metadata_func(regex, file):
                item["_id"] = id
                contents.append(item)
                id += 1

            contents.append(item)

        except UnicodeDecodeError:
            pass

    for id, file in enumerate(list_notebooks):

        try:

            for item in metadata_notebook(file):
                item["_id"] = id
                contents.append(item)
                id += 1

            contents.append(metadata_full_notebook(file, id))
            id += 1

        except UnicodeDecodeError:
            pass

    helpers.bulk(es, contents)


def create_app():

    app = Flask(__name__)

    app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True
    app.config["SECRET_KEY"] = "the quick brown fox jumps over the lazy dog"
    app.config["CORS_HEADERS"] = "Content-Type"

    cors = CORS(app, resources={r"/foo": {"origins": "*"}})
    app.config["CORS_HEADERS"] = "Content-Type"

    es = Elasticsearch()

    # Init index
    for index in ["notebook", "function", "full_notebook", "classe"]:
        if not es.indices.exists(index=index):
            es.indices.create(index=index)

    @app.route("/init/")
    @cross_origin(origin="localhost", headers=["Content-Type", "Authorization"])
    def init():

        for index in ["notebook", "function", "full_notebook", "classe"]:
            es.delete_by_query(index=index, body={"query": {"match_all": {}}})
            es.indices.refresh(index=index)

        list_files = walk()
        list_notebooks = walk(extension=".ipynb")
        scan_files(es, list_files, list_notebooks)

        for index in ["notebook", "function", "full_notebook", "classe"]:
            es.indices.refresh(index=index)

        return jsonify({"status": "Index intialized."}), 200

    @app.route("/get/<content>", methods=["GET"])
    @cross_origin(origin="localhost", headers=["Content-Type", "Authorization"])
    def get(content):

        match = []

        for index in ["notebook", "function", "full_notebook", "classe"]:

            response = es.search(
                index=index,
                body={"query": {"query_string": {"query": f"*{content}*", "fields": ["content"]}}},
            )

            for r in response["hits"]["hits"]:
                match.append(r["_source"])

        return jsonify(match), 200

    return app
