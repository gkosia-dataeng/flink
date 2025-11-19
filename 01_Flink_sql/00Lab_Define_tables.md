## Flink SQL Client Tutorial

Follow these steps to explore catalogs, databases, and tables in Flink SQL:

1. **Enter the SQL Client container**: ```  docker-compose run sql-client ```

2. **Check existing catalogs**:  ``` SHOW CATALOGS;  ``` \
   *By default, there is only one catalog: `default_catalog`.*

3. **Check existing databases**: ```SHOW DATABASES;```

4. **Create a new database**:   ``` CREATE DATABASE SQL_LAB; ```

5. **Switch to the new database**:  ``` USE SQL_LAB; ```

6. **Create the `customers` table**:  
      
      ```
       CREATE TABLE SQL_LAB.customers (
           id INT,
           name STRING,
           country STRING
       ) WITH (
           'connector' = 'kafka',
           'topic' = 'json-customers',
           'properties.bootstrap.servers' = 'kafka:19092',
           'properties.group.id' = 'flink_group',
           'scan.startup.mode' = 'earliest-offset',
           'format' = 'json',
           'json.fail-on-missing-field' = 'false',
           'json.ignore-parse-errors' = 'true'
       ); 
       

7. **View the metadata of the `customers` table**:   ``` DESCRIBE customers;```

8. **Run a streaming query on `customers`**:   ```SELECT * FROM customers;```

9. **Create the `transactions` table**:  
      ``` 
      CREATE TABLE SQL_LAB.transactions (
           id INT,
           cust_id INT,
           create_time TIMESTAMP,
           amount DOUBLE
       ) WITH (
           'connector' = 'kafka',
           'topic' = 'json-transactions',
           'properties.bootstrap.servers' = 'kafka:19092',
           'properties.group.id' = 'flink_group',
           'scan.startup.mode' = 'earliest-offset',
           'format' = 'json',
           'json.fail-on-missing-field' = 'false',
           'json.ignore-parse-errors' = 'true'
       );

10. **Query the `transactions` table**:  ``` SELECT * FROM transactions; ``` 

11. **Get the definition of `transactions` table**: ``` SHOW CREATE TABLE transactions; ```

