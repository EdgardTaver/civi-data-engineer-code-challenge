# Code challenge for Data Engineer. 

# Introduction

Using any technology, tool, languages, frameworks that you want, create an ETL (Extract, transform, load) process to extract data.

Create a second database called `dwh` and populate using any ETL strategy to answer these questions: 

- How many users are not in any region?

- How many markers does each region have?

- What are the top N regions with the most users?

You can write the SQL queries to answer these question.

If you want you can create reports/visualizations.

You can show other insights from the data.

There are two data sources, the `users.json` file and the database.

To startup the database server you can run `make up` and connect to `postgres://postgres:postgres@localhost:5400/postgres`. Here you will find two tables `regions` and `markers`.

The `users.json` is in data folder.

Good luck!

# Solution

## Requirements

- Must have **Python 3.8.3** or higher installed.
- Run `make install` to create python dependencies.

## How to run

There's a **main pipeline** that reads all the raw data (the `users.json` file and the data in the default `postgres` database), transforms it and loads it into the `dwh` database.

This main pipeline will always ensure a **clean start**. That is: it will drop any existing data in the `dwh` database and recreate everything from scratch.

To run it, type this command:

```sh
make run
```

If you later wish to **drop the DWH database**, run this command:

```sh
make drop
```
