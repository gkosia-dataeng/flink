## Event time and watermark

Follow these steps to explore time window aggregations:

1. **Enter the SQL Client container**: ```  docker-compose run sql-client ``` or ``` make sql-cl```

2. **Create the transactions table using watermark**: 
   ```
      CREATE TABLE transactions (
               id INT,
               cust_id INT,
               create_time TIMESTAMP(3),
               amount DOUBLE,
               ts_proctime AS PROCTIME(),
               WATERMARK FOR create_time AS create_time - INTERVAL '5' MINUTE
            ) WITH (
               'connector' = 'kafka',
               'topic' = 'json-transactions',
               'properties.bootstrap.servers' = 'kafka:19092',
               'properties.group.id' = 'flink_group',
               'scan.startup.mode' = 'latest-offset',
               'format' = 'json',
               'json.fail-on-missing-field' = 'false',
               'json.ignore-parse-errors' = 'true'
            );
   ```

3. **Run a window grouping query and inspect the output for which events has been ignored (late events) and when the message emited**:

    ```
    SELECT 
          window_start
         ,window_end
         ,window_time 
         ,COUNT(*)    AS num_of_messages
         ,SUM(amount) AS amount_by_window
      FROM TABLE( 
         TUMBLE(
               TABLE transactions
               ,DESCRIPTOR(create_time)
               ,INTERVAL '5' MINUTES)
               )
      group by 
          window_start
         ,window_end
         ,window_time;
    ```