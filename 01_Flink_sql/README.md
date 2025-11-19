## Flink SQL Overview

Flink SQL provides a powerful and intuitive way to process data in **real time**.  
Using the SQL API, you define **sources** and **sinks** as *tables*, then write SQL queries to transform and enrich data before inserting it into your sink tables.

Flink SQL includes a rich collection of functions and operations that support both **stateless** and **stateful** transformations, making it suitable for a wide range of streaming use cases.

---

## Running the SQL Client

To start the Flink SQL Client locally:

1. Start the `local_env` environment. [local_env](../local_env/README.md)
2. Launch the interactive SQL client inside the container:
   ```bash
   docker-compose run sql-client
   ```

## Resources:

   [getting-started-with-apache-flink-sql](https://www.confluent.io/blog/getting-started-with-apache-flink-sql/) \
   [stream-processing-exercise](https://developer.confluent.io/courses/apache-flink/stream-processing-exercise/)