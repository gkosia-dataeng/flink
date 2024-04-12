/*
    Kafka event:
        Metadata: topic, partition, offset, timestamp
        Header:   app-specific key/value
        Key: serialized bytes in some format from producer
        Value: serialized bytes in some format from producer

    In Flink:
        Map Flink tables to Kafka topics
        Flink need to know:
            connector: kafka
            properties.bootstrap.servers
            topic
            key.format
            value.format
*/

/*
    Create topics: 
        kafka-topics --create --topic flink_source --bootstrap-server kafka:19092
        kafka-topics --create --topic flink_sink --bootstrap-server kafka:19092

    Produce events in source: 
        kafka-console-producer --bootstrap-server kafka:19092 --topic flink_source
        
        Example: {"user":"a", "points": "10"}
*/

-- Create the flink source table 
CREATE TABLE flink_source (
  `user`    STRING,
  `points`  INT,
  `ev_time` TIMESTAMP_LTZ(3) METADATA FROM 'timestamp' 
) WITH (
  'connector' = 'kafka',
  'topic' = 'flink_source',
  'properties.group.id' = 'demoGroup',
  'scan.startup.mode' = 'earliest-offset',
  'properties.bootstrap.servers' = 'kafka:19092',
  'value.format' = 'json'
);