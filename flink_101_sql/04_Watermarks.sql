/*
    kafka-topics --create --topic flink_source_random --bootstrap-server kafka:19092
*/


/*
    WATERMARK FOR `ts` AS ts - INTERVAL '5' SECOND: 
        create a watermark on ts column 
        The watermark created with 5 seconds to match the out of order ts of faker
*/
-- Create the Faker stream table
CREATE TABLE `faker_stream` (
  `url` STRING,
  `user_id` STRING,
  `browser` STRING,
  `ts` TIMESTAMP(3),
  WATERMARK FOR `ts` AS ts - INTERVAL '5' SECOND
)
WITH (
  'connector' = 'faker',
  'rows-per-second' = '10',
  'fields.url.expression' = '/#{GreekPhilosopher.name}.html',
  'fields.user_id.expression' = '#{numerify ''user_##''}',
  'fields.browser.expression' = '#{Options.option ''chrome'', ''firefox'', ''safari'')}',
  'fields.ts.expression' =  '#{date.past ''5'',''1'',''SECONDS''}'
); 

/*
    Tuble faker_stream and use the ts as event time
*/
SELECT
  window_start, count(url) AS cnt
FROM TABLE(
  TUMBLE(TABLE faker_stream, DESCRIPTOR(ts), INTERVAL '1' SECOND))
GROUP BY window_start;



/*
    Scenario: Pattern matching with MATCH_RECOGNIZE
              Find users that do first A action and then B action AND THEN C action 
              To find that pattern weneed to sort the actions based on event time


    MATCH_RECOGNIZE
*/
SELECT *
FROM faker_stream
    MATCH_RECOGNIZE (
      PARTITION BY user_id
      ORDER BY ts
      MEASURES
        A.browser AS browser1,
        B.browser AS browser2,
        A.ts AS ts1,
        B.ts AS ts2
      PATTERN (A B) WITHIN INTERVAL '1' SECOND
      DEFINE
        A AS true,
        B AS B.browser <> A.browser
    );