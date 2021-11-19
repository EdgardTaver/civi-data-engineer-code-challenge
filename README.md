## Code challenge for Data Engineer. 

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
