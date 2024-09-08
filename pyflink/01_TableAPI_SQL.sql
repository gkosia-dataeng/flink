   SET 'sql-client.execution.result-mode' = 'tableau';

   CREATE TABLE deals_topic (
         deal_id                INT,
         platform_position_id   INT,
         login                  INT,
         server                 STRING,
         execution_time         TIMESTAMP_LTZ(3) METADATA FROM 'timestamp',
         position_impact        INT,
         trade_direction        INT,
         volumn                 INT,
         profit                 INT
    ) WITH (
        'connector' = 'kafka',
        'topic' = 'source_postgresql.public.deals',
        'properties.bootstrap.servers' = 'kafka:19092',
        'properties.group.id' = 'tradesProcessor',
        'format' = 'debezium-json',
        'scan.startup.mode' = 'earliest-offset'
    );

    select * from deals_topic;


    CREATE TABLE accounts_topic (
         login INT,
         login_group STRING,
         user_id INT
    ) WITH (
        'connector' = 'kafka',
        'topic' = 'source_postgresql.public.mt4account',
        'properties.bootstrap.servers' = 'kafka:19092',
        'properties.group.id' = 'tradesProcessor',
        'format' = 'debezium-json',
        'scan.startup.mode' = 'earliest-offset'
    );
    
    SELECT * FROM accounts_topic;

    CREATE TABLE deals_enreached (
         deal_id                INT,
         platform_position_id   INT,
         login                  INT,
         execution_time         TIMESTAMP_LTZ(3) METADATA FROM 'timestamp',
         profit                 INT,
         login_group STRING,
         user_id INT
    ) WITH (
        'connector' = 'kafka',
        'topic' = 'deals-enreached',
        'properties.bootstrap.servers' = 'kafka:19092',
        'properties.group.id' = 'tradesProcessor',
        'format' = 'debezium-json',
        'scan.startup.mode' = 'earliest-offset'
    );


    SELECT 
         d.deal_id
        ,d.platform_position_id
        ,d.login
        ,execution_time
        ,d.profit
        ,a.login_group
        ,a.user_id
    FROM deals_topic d
    LEFT JOIN accounts_topic a
      ON d.login = a.login;


    INSERT INTO deals_enreached
    SELECT 
         d.deal_id
        ,d.platform_position_id
        ,d.login
        ,execution_time
        ,d.profit
        ,a.login_group
        ,a.user_id
    FROM deals_topic d
    LEFT JOIN accounts_topic a
      ON d.login = a.login;
