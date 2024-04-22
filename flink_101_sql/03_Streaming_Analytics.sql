/*
    Streaming Analytics: Calculate statistics realtime on a stream 

    kafka-topics --create --topic flink_source_random --bootstrap-server kafka:19092
    
*/

-- Create the Faker stream table
CREATE TABLE `faker_stream` (
  `url` STRING,
  `user_id` STRING,
  `browser` STRING,
  `ts` TIMESTAMP(3)
)
WITH (
  'connector' = 'faker',
  'rows-per-second' = '10',
  'fields.url.expression' = '/#{GreekPhilosopher.name}.html',
  'fields.user_id.expression' = '#{numerify ''user_##''}',
  'fields.browser.expression' = '#{Options.option ''chrome'', ''firefox'', ''safari'')}',
  'fields.ts.expression' =  '#{date.past ''5'',''1'',''SECONDS''}'
); 


-- Create the flink flink_source_random to point to flink_source_random kafka topic
CREATE TABLE flink_source_random_in_kafka (
  `url` STRING,
  `user_id` STRING,
  `browser` STRING,
  `ts` TIMESTAMP(3)
) WITH (
  'connector' = 'kafka',
  'topic' = 'flink_source_random',
  'properties.group.id' = 'demoGroup',
  'scan.startup.mode' = 'earliest-offset',
  'properties.bootstrap.servers' = 'kafka:19092',
  'value.format' = 'json'
);


-- Pipeline: insert data from faker stream to kafka topic
INSERT INTO flink_source_random_in_kafka SELECT * FROM faker_stream


-- Create the analytics job: this will save in state a record for each second 
-- NOT SAFE because the state will have infinite records as it runs and will hit the state storage limit
SELECT
  FLOOR(ts TO SECOND) AS window_start,
  count(url) as cnt
FROM flink_source_random_in_kafka
GROUP BY FLOOR(ts TO SECOND);

-- SAFE state because there are small number of browser so if we leave it run forever 
-- Will not hit the state storage limit
SELECT
  browser,
  count(url) as cnt
FROM flink_source_random_in_kafka
GROUP BY browser;


-- Using Windowing
-- The state of a window will be cleaned up once they are no longer change
-- For Windowing we need an append only table and a timestamp column
-- Processing time: the time the event is processed (we are sure that the time is advancing(next event will have later time))
-- Event time: when it occured in the source system (we are NOT SURE that the time is advancing(next event might have EARLIER time))

/*
    Working with Processing time:
        We need to attach to the event a calculated column (not a physical) that is the PROCTIME()
*/
ALTER TABLE faker_stream ADD `proc_time` AS PROCTIME();
describe faker_stream;   -- name, type. null, key, extras, watermark

-- Analytics using windows
-- TUMBLE  table value function
--      params: 
--              table descriptor
--              the column will be used for time
--              interval of window
--      output:
--             window_start, window_end, window_time
-- So we can use the window_* columns to group by window

-- Additional window function HOP, CUMULATE, and SESSION windows
SELECT
  window_start, count(url) AS cnt
FROM TABLE(
  TUMBLE(TABLE faker_stream, DESCRIPTOR(proc_time), INTERVAL '1' SECOND))
GROUP BY window_start;


