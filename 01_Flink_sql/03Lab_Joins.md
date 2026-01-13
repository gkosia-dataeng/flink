1. **Create the `customers` table**:  
      
      ```
       CREATE TABLE customers (
           id INT,
           name STRING,
           country STRING
       ) WITH (
           'connector' = 'kafka',
           'topic' = 'json-customers',
           'properties.bootstrap.servers' = 'kafka:19092',
           'properties.group.id' = 'flink_group',
           'scan.startup.mode' = 'latest-offset',
           'format' = 'json',
           'json.fail-on-missing-field' = 'false',
           'json.ignore-parse-errors' = 'true'
       ); 

    ```


2. **Create the `transactions` table**:  
      ``` 
      CREATE TABLE transactions (
           id INT,
           cust_id INT,
           create_time TIMESTAMP,
           amount DOUBLE
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

3. **Join the two streams using `INNER JOIN`**: 

    ```
        SELECT 
             c.id
            ,c.name
            ,t.create_time
            ,t.amount
        FROM customers as c
        INNER JOIN transactions as t
          ON c.id = t.cust_id;


4. 