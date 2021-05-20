## Perdu

Perdu is a local and minimalist search engine for python code. Perdu explores all python scripts and 
notebooks to index them with ElasticSearch. The perimeter of Perdu is limited for personnal usage 
to a local machine.

![](perdu.gif)

#### Installation

```sh
pip install git+https://github.com/raphaelsty/perdu
```

We need to set the PERDU environment variable. All python and notebook files
contained in the directory and subdirectories of the environment variable will be indexed.

```sh
export PERDU=/PATH_YOU_WANT_TO_INDEX
```

For example, I will index my files in the Documents sub-directory `export PERDU=/Users/raphaelsourty/Documents`.

#### Quick start

It is necessary to have ElasticSearch installed to run the search engine. More details [here for installation](https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html).

To start the application, you must first start the ElasticSearch server with the command:

```sh
elasticsearch
```

To start the flask application and open the search engine, run:

```sh
perdu start
```

The flask app will run by default on the port `5000`.

#### Index

To index documents especially at the first startup, run:

```sh
perdu scan
```

It is necessary to have launched the application with `perdu start` to index the documents.

#### Debug
Sometimes an application runs in the background and we are forced to close the process without being able to use ctrl+c.

To find the process ID (PID) ElasticSearch:

```sh
lsof -i:9200
```

To find the process identifier (PID) Flask:

```sh
lsof -i:5000
```

To force the process to stop:

```sh
kill -9 <PID>
```