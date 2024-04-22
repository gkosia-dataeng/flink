/*
    flink-faker is a mock data generator designed to be used with Flink
*/

CREATE TABLE `bounded_pageviews` (
  `url` STRING,
  `user_id` STRING,
  `browser` STRING,
  `ts` TIMESTAMP(3)
)
WITH (
  'connector' = 'faker',
  'number-of-rows' = '500',
  'rows-per-second' = '100',
  'fields.url.expression' = '/#{GreekPhilosopher.name}.html',
  'fields.user_id.expression' = '#{numerify ''user_##''}',
  'fields.browser.expression' = '#{Options.option ''chrome'', ''firefox'', ''safari'')}',
  'fields.ts.expression' =  '#{date.past ''5'',''1'',''SECONDS''}'
);


-- By default flink runs in streaming mode
-- Using the below we are switching to batch mode
set 'execution.runtime-mode' = 'batch';
-- switch back to streaming
set 'execution.runtime-mode' = 'streaming';

-- sql client will display each message of stream that receives from FlinkSQL runtime
-- the flink continusly updating the results as process the input stream
set 'sql-client.execution.result-mode' = 'changelog'; -- table (default), tableau

/*
    Create unbounded stream with faker: if faker source isn't configured with a number-of-rows it will stream continuesly new data
*/
CREATE TABLE `pageviews` (
  `url` STRING,
  `user_id` STRING,
  `browser` STRING,
  `ts` TIMESTAMP(3)
)
WITH (
  'connector' = 'faker',
  'rows-per-second' = '100',
  'fields.url.expression' = '/#{GreekPhilosopher.name}.html',
  'fields.user_id.expression' = '#{numerify ''user_##''}',
  'fields.browser.expression' = '#{Options.option ''chrome'', ''firefox'', ''safari'')}',
  'fields.ts.expression' =  '#{date.past ''5'',''1'',''SECONDS''}'
);

-- alter the 'rows-per-second' to send slower the data
ALTER TABLE `pageviews` SET ('rows-per-second' = '10');

-- see the job graph
EXPLAIN select count(*) from pageviews