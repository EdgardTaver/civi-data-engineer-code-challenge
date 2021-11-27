# Code Challenge for Data Engineer

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

## Queries

### 1. How many users are not in any region?

Query:

```sql
SELECT COUNT(id) AS users_not_in_any_region FROM dwh.users
WHERE 1=1
AND region IS NULL
```

Expected result:

users_not_in_any_region|
-----------------------|
692                    |

### 2. How many markers does each region have?

Query:

```sql
SELECT region, count(region)
FROM dwh.markers u 
WHERE region IS NOT NULL
GROUP BY region
ORDER BY 2 DESC
```

Expected result:

region             | count|
-------------------|------|
República          | 43   |
Bom Retiro         | 31   |
Jabaquara          | 26   |
Cachoeirinha       | 25   |
Santana            | 24   |
_90 more rows_     | ...  |

### 3. What are the top N regions with the most users?

Query:

```sql
WITH params AS (SELECT 5 AS N)
SELECT region, count(region) FROM dwh.users
WHERE region IS NOT NULL 
GROUP BY region
ORDER BY 2 DESC
LIMIT (SELECT N FROM params)
```

> Change the first line to set whatever value you wish for `n`.

Expected result:

region          | count |
----------------|-------|
Marsilac        | 14    |
Parelheiros     | 11    |
Grajaú          | 8     |
Itaim Paulista  | 4     |
Parque do Carmo | 4     |

## Assumptions

- The following assumptions were considered for _Users_:
    - A `username` is **unique**.
    - If a _User_ has `NULL` latitude or `NULL` longitude, it is considered an invalid entity and it will not be added to _DWH_.
    - The position of a _User_ may be **updated** at any time. Therefore, if we attempt to insert a user into _DWH_, but the username already exists, then its position must be updated.

- The following assumptions were considered for _Regions_ and _Markers_:
    - Only soft deletions are allowed (entities are not really dropped from the database).
    - The soft-delete is done by setting the `deleted_at` field to a valid date.
    - A soft deleted region is **not** considered a valid region, therefore it is not loaded into _DWH_.

## Considerations for the solution presented

The full pipeline describe in the `main.py` script always destroys the data in the DWH database and then rebuilds it from the scratch. This is just for the sake of showing how the process works end to end.

In a real world scenario, the pipeline would not destroy the existing data, as rebuilding _everything_ from scratch is a solution that would not scale well.

All the migrations are _idempotent_, meaning that they can be run multiple times without any side effects. This means that we do **not** really need to track which migrations were already run. This works really well for this small example, but in a real world scenarion, we could have more complex and/or specific migrations in which such behaviour would not be desirable.

The process to load _Regions_ and _Markers_ into the **DWH** is also **idempotent**, as it will ensure that the `ID` is **unique**. It will insert any new _Region_ or _Marker_, as well as update existing ones and drop those that were soft deleted. This process should ensure consistency in the DWH, **but it has two shortcomings**:
- It will always either insert a row or update an existing one, meaning that it is guaranteed that it will run one of these operations for every single row. This may lead to poor performance on big datasets. **It may be possible to work on optimization for this**.
- It depends on the soft deletion to always work. If, for instance, a given _Region_ or _Marker_ that exists in DWH is **dropped** (instead of being soft deleted) from the raw data tables, it will remain in the DWH database. This may lead to inconsistency in the DWH.

The process to load _Users_ ensures idempotence by assuming that the username is **unique**. It will insert any new _User_, as well as update existing ones. However, it is _not_ able to drop users. The `users.json` raw data file does _not_ indicate any sort of soft deletion.

If we assume that this file is the main source of data for _Users_, and that if a given username is removed from it, we should remove it from the DWH, then we could implement an additional step in the `LoadUsersCommand` in which it compares the full table from DWH and the full table obtained in the JSON (for instance: using the `.isin()` method from `pandas`) and checks the usernames that could not be found in the JSON.

All tables in the DWH have a `deleted_at` column. This makes the DWH consistent with the data models found in the raw data, which is a good thing (consider that analysts and developers may query both the raw data as well as the DWH expecting similar attributes and logic). But since we have defined that a soft deleted `Region` and `Marker` means an invalid entity, which is _not_ loaded in the DWH, and there's no mechanism to handle deletion of `Users`, then there's really **no** use for the `delete_at` attribute in the DWH tables.

## View

A basic visualization of the queries are available as a Jupyter Notebook (`view.ipynb`) and a PDF file (`view.pdf`).