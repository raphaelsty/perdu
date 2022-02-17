## Perdu

Perdu is a local and minimalist search engine for python code. Perdu explores all python scripts and
jupyter notebooks to index them with Cherche. The perimeter of Perdu is limited for personnal usage
to a local machine.

![](perdu.gif)

#### Installation

```sh
pip install git+https://github.com/raphaelsty/perdu
```

UI dependancies:

```sh
npm install highlight.js@10.7.1
npm install vue@2
```

#### Quick start

You will first need to index documents. The `-p` parameter allows to choose the set of folders to be indexed.

```sh
perdu scan -p .
```

To start the app, run:

```sh
perdu start
```

The flask app will run by default on the port `5000`.

To open the web app, run:

```sh
perdu open
```

You can close the app using `ctrl+c`.

#### Index

It is necessary to have launched the application with `perdu start` to index the documents.

#### Debug

The application runs in the background and we may be forced to close the process without being able to use `ctrl+c`. To find the process identifier (PID) Flask:

```sh
lsof -i:5000
```

To force the process to stop:

```sh
kill -9 <PID>
```
