CREATE DATABASE IF NOT EXISTS SQL_LAB;

-- Use the database
USE SQL_LAB;

-- Create customers table
CREATE TABLE customers (
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

-- Create transactions table
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
    'scan.startup.mode' = 'earliest-offset',
    'format' = 'json',
    'json.fail-on-missing-field' = 'false',
    'json.ignore-parse-errors' = 'true'
);

-- Create upsert-kafka sink
CREATE TABLE customer_sum (
    cust_id INT PRIMARY KEY NOT ENFORCED,
    amount DOUBLE
) WITH (
    'connector' = 'upsert-kafka',
    'topic' = 'json-output',
    'properties.bootstrap.servers' = 'kafka:19092',
    'properties.group.id' = 'flink_group',
    'key.format' = 'json',
    'value.format' = 'json'
);


INSERT INTO customer_sum
SELECT
    t.cust_id,
    SUM(t.amount) AS amount
FROM transactions t
INNER JOIN customers c
    ON t.cust_id = c.id
WHERE c.country = 'USA'
GROUP BY t.cust_id;