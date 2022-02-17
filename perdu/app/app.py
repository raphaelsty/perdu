import os
import pickle
import re
import time

from cherche import retrieve
from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
from nbformat import NO_CONVERT, read
from sklearn.feature_extraction.text import TfidfVectorizer

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
    "init_pipeline",
]


def walk(path, extension):
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
            "id": file,
            "type": "function",
            "date": time.ctime(os.path.getmtime(file)),
            "content": func.group(0),
        }


def metadata_notebook(file):
    """Read code of notebooks."""
    with open(file) as fp:
        notebook = read(fp, NO_CONVERT)

    if "cells" in notebook:
        cells = [cell for cell in notebook["cells"] if cell["cell_type"] == "code"]
        for cell in cells:
            yield {
                "id": file,
                "type": "notebook",
                "date": time.ctime(os.path.getmtime(file)),
                "content": cell["source"],
            }


def metadata_full_notebook(file):
    """Read code of notebooks."""
    with open(file) as fp:
        notebook = read(fp, NO_CONVERT)

    if "cells" in notebook:
        cells = [cell for cell in notebook["cells"] if cell["cell_type"] == "code"]

        content = ""
        for cell in cells:
            content += "\n" + cell["source"]

        return {
            "id": f"{file}_full_notebook",
            "type": "full_notebook",
            "date": time.ctime(os.path.getmtime(file)),
            "content": content,
        }


def metadata_file(file):
    """Read files and export complete file."""
    with open(file) as f:
        content = f.read()

    return {
        "id": f"{file}_full_script",
        "type": "full_script",
        "date": time.ctime(os.path.getmtime(file)),
        "content": content,
    }


def scan_files(list_files, list_notebooks):
    """Scan python files and notebooks and index them using ElasticSearch."""
    files, functions, cells, notebooks = [], [], [], []

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

    for file in list_files:

        try:

            files.append(metadata_file(file))

            for item in metadata_func(regex, file):
                functions.append(item)

        except UnicodeDecodeError:
            pass

    for file in list_notebooks:

        try:

            for item in metadata_notebook(file):
                cells.append(item)

            notebooks.append(metadata_full_notebook(file))

        except UnicodeDecodeError:
            pass

    return cells, notebooks, functions, files


def create_app(here):

    app = Flask(__name__)
    app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True
    app.config["CORS_HEADERS"] = "Content-Type"
    CORS(app)

    with open(os.path.join(here, "search.pkl"), "rb") as store:
        search = pickle.load(store)

    @app.route("/get/<content>", methods=["GET"])
    @cross_origin()
    def get(content):
        match = search(content)
        return jsonify([doc for doc in match]), 200

    return app


def init_pipeline(p, here):
    list_files = walk(path=p, extension=".py")
    list_notebooks = walk(path=p, extension=".ipynb")

    search = None
    duplicates = {}
    for documents in scan_files(list_files, list_notebooks):

        filter = []
        for doc in documents:
            if doc["content"] in duplicates:
                continue
            elif doc["content"]:
                duplicates[doc["content"]] = True
                filter.append(doc)

        if search is None and filter:
            search = (
                retrieve.TfIdf(
                    key="id",
                    on=["content", "id"],
                    documents=filter,
                    tfidf=TfidfVectorizer(lowercase=True, ngram_range=(3, 7), analyzer="char_wb"),
                    k=5,
                )
                + filter
            )
        elif filter:
            search = search | (
                retrieve.TfIdf(
                    key="id",
                    on=["content", "id"],
                    documents=filter,
                    tfidf=TfidfVectorizer(lowercase=True, ngram_range=(3, 7), analyzer="char_wb"),
                    k=5,
                )
                + filter
            )

    with open(os.path.join(here, "search.pkl"), "wb") as store:
        pickle.dump(search, store)
