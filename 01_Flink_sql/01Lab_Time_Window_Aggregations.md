## Time Window Aggregations Lab

Follow these steps to explore time window aggregations:

1. **Enter the SQL Client container**: ```  docker-compose run sql-client ``` or ``` make sql-cl```

2. **Create the transactions table**: 
   ```
      CREATE TABLE transactions (
               id INT,
               cust_id INT,
               create_time TIMESTAMP(3),
               amount DOUBLE,
               ts_proctime AS PROCTIME(),
               WATERMARK FOR create_time AS create_time - INTERVAL '5' SECOND
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


***IMPORTANT NOTE: BECAUSE WE ARE USING WATERMARKS (EVENT TIME PROCESSING) FLINK WILL EMIT THE MESSAGE ONLY IF THE TIME OF THE GROUP PASSED BASED ON create_time***

3. **Run the query using the Tumpling window**: 

   The second argument of the TUMBLE is the timecol which should be a time attribute type. \
   A simple TIMESTAMP column (create_time) is not accepted, should be converted to event time attribute by specifing a watermark on it. 
   
   ``WATERMARK FOR create_time AS create_time - INTERVAL '5' SECOND`` \
   OR \
   Another option is to define a processing time column and use it as timecol 

   ```
      -- Each message will be enriched with the columns window_start, window_end, window_time based on the timecol value and the INTERVAL

      SELECT * 
      FROM TABLE( 
         TUMBLE(
               TABLE transactions
               ,DESCRIPTOR(create_time)
               ,INTERVAL '10' MINUTES)
               );

      -- We can use these column s to make aggregations by window
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
               ,INTERVAL '10' MINUTES)
               )
      group by 
          window_start
         ,window_end
         ,window_time;

   ```


   
4. **In a separeted terminal run the data producer to populate few transaction in the kafka topic and insect the results in flink client**:  ```make data-t```



5. **Create the table using the Hopping/Sliding window**: 

   ```
      SELECT 
       cust_id,
       window_start,
       window_end,
       COUNT(*)    AS num_of_messages,
       SUM(amount) AS amount_by_window
      FROM TABLE(
         HOP(
             TABLE transactions
            ,DESCRIPTOR(create_time), INTERVAL '5' MINUTES, INTERVAL '10' MINUTES
            )
      )
      GROUP BY 
       cust_id,
       window_start,
       window_end;
   
   
   ```


6. **In a separeted terminal run the data producer to populate few transaction in the kafka topic and insect the results in flink client**:  ```make data-t```


7. **Create the table using the Session window**: 

   ```
      SELECT 
       window_start,
       window_end,
       COUNT(*)    AS num_of_messages,
       SUM(amount) AS amount_by_window
      FROM TABLE(
         SESSION(
             TABLE transactions
            ,DESCRIPTOR(create_time), INTERVAL '5' MINUTES
            )
      )
      GROUP BY 
       window_start,
       window_end;
   
   
   ```


8. **In a separeted terminal run the data producer to populate few transaction in the kafka topic and insect the results in flink client**:  ```make data-t```