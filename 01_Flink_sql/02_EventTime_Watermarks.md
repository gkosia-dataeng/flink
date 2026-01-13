## Event Time vs. Processing Time

**Event Time**  
Event time is derived from a timestamp contained within each event. The stream’s notion of time progresses according to the timestamps of the events as they arrive.

**Processing Time**  
Processing time is the system time at the moment when an event is processed by Flink.

---

## Watermarks

Watermarks are special markers inserted into the stream to indicate the progress of event time.
They are calculated based on the most recent time seen - allowed_latensy_interval
The watermark tells that the stream is completed up-to but not including watermark time
Earlier events than watermark are ignored

Watermark are calculated by source for each partition
The source operator will produce the minimum watermark from the partitions its reading
The watermark of the stream is the minimum watermark from sources


The window will not produce the results intil window end time  + allowed_latency_time


 They serve several important roles:

- They tell Flink the *current* event time.
- Any event whose event time is **earlier than the current watermark** is considered *late*.
- Watermarks allow Flink to handle late-arriving data.  
- Defining a watermark also means defining an **allowed lateness** interval.  
  - If an event arrives with `event_time > watermark`, it is included in computations.  
  - If it arrives **older than `event_time window end + allowed_late_interval`**, it is considered late and ignored.

---

## Defining a Watermark on a Table

```sql
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

## Explanation

In this example:

- The **event time** of the stream is driven by `create_time`.
- The **watermark** is defined as `create_time - 5 seconds`, meaning Flink allows events to arrive up to **5 seconds late**.
- If an event arrives with a `create_time` earlier than **current event time − 5 seconds**, it is considered **late** and will be ignored by Flink.