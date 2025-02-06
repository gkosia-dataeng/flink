from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment
from StreamJoiners import OrdersDealsJoin, PositionsOrdersJoin, BroadcastEnrichmentInfo, union_brdcst_messages_state_descr, logger




env = StreamExecutionEnvironment.get_execution_environment()
t_env = StreamTableEnvironment.create(env)


# Define the tables to ingest the data from kafka
t_env.execute_sql("""CREATE TABLE symbol (
        symbol_id INT,
        name STRING,
        update_time TIMESTAMP(3),
        WATERMARK FOR update_time AS update_time - INTERVAL '10' MINUTE
    ) WITH (
        'connector' = 'kafka',
        'topic' = 'source-symbol',
        'properties.bootstrap.servers' = 'kafka:19092',
        'value.format' = 'json',
        'properties.group.id' = 'test-group',
        'scan.startup.mode' = 'earliest-offset'
    )
    """)

t_env.execute_sql("""CREATE TABLE `position` (
        position_id INT,
        symbol_id INT,
        trader_id INT,
        open_time TIMESTAMP(3),
        status STRING,
        update_time TIMESTAMP(3),
        WATERMARK FOR update_time AS update_time - INTERVAL '10' MINUTE
    ) WITH (
        'connector' = 'kafka',
        'topic' = 'source-position',
        'properties.bootstrap.servers' = 'kafka:19092',
        'value.format' = 'json',
        'properties.group.id' = 'test-group',
        'scan.startup.mode' = 'earliest-offset'
    )
    """)

t_env.execute_sql("""CREATE TABLE `order` (
        order_id INT,
        position_id INT,
        type STRING,
        update_time TIMESTAMP(3),
        WATERMARK FOR update_time AS update_time - INTERVAL '10' MINUTE
    ) WITH (
        'connector' = 'kafka',
        'topic' = 'source-order',
        'properties.bootstrap.servers' = 'kafka:19092',
        'value.format' = 'json',
        'properties.group.id' = 'test-group',
        'scan.startup.mode' = 'earliest-offset'
    )
    """)

t_env.execute_sql("""CREATE TABLE deal (
        deal_id INT,
        order_id INT,
        trader_id INT,
        profit DOUBLE,
        create_date TIMESTAMP(3),
        update_time TIMESTAMP(3),
        WATERMARK FOR update_time AS update_time - INTERVAL '10' MINUTE
    ) WITH (
        'connector' = 'kafka',
        'topic' = 'source-deal',
        'properties.bootstrap.servers' = 'kafka:19092',
        'value.format' = 'json',
        'properties.group.id' = 'test-group',
        'scan.startup.mode' = 'earliest-offset'
    )
    """)

t_env.execute_sql("""CREATE TABLE trader (
        trader_id INT,
        login INT,
        trader_group_id INT,
        create_date TIMESTAMP(3),
        update_time TIMESTAMP(3),
        WATERMARK FOR update_time AS update_time - INTERVAL '10' MINUTE
    ) WITH (
        'connector' = 'kafka',
        'topic' = 'source-trader',
        'properties.bootstrap.servers' = 'kafka:19092',
        'value.format' = 'json',
        'properties.group.id' = 'test-group',
        'scan.startup.mode' = 'earliest-offset'
    )
    """)

t_env.execute_sql("""CREATE TABLE trader_group (
        trader_group_id INT,
        trader_group_name STRING,
        create_date TIMESTAMP(3),
        update_time TIMESTAMP(3),
        WATERMARK FOR update_time AS update_time - INTERVAL '10' MINUTE
    ) WITH (
        'connector' = 'kafka',
        'topic' = 'source-trader-group',
        'properties.bootstrap.servers' = 'kafka:19092',
        'value.format' = 'json',
        'properties.group.id' = 'test-group',
        'scan.startup.mode' = 'earliest-offset'
    )
    """)



# trader, trader_group and symbols will be broadcasted
# create a unified structure and union the streams 
# We need one stream becasue flink does not support to connect multiple Broadcasted stream with another stream
# So we will union the broadcasted messages to one stream and then connect and join them with the other data using a CoProcessFunction

traders = t_env.sql_query(""" 
                            SELECT 
                                 trader_id                  AS trader_id
                                ,login                      AS login
                                ,trader_group_id            AS trader_group_id
                                ,CAST(NULL AS STRING)       AS trader_group_name
                                ,CAST(NULL AS INT)          AS symbol_id
                                ,CAST(NULL AS STRING)       AS symbol_name
                                ,CAST('trader' AS STRING)   AS src
                            FROM trader
                        """)

trader_groups = t_env.sql_query(""" 
                                    SELECT 
                                        CAST(NULL  AS INT)              AS trader_id
                                       ,CAST(NULL  AS INT)              AS login
                                       ,trader_group_id                 AS trader_group_id
                                       ,trader_group_name               AS trader_group_name
                                       ,CAST(NULL AS INT)               AS symbol_id
                                       ,CAST(NULL AS STRING)            AS symbol_name
                                       ,CAST('trader_group' AS STRING)  AS src
                                    FROM trader_group
                                """)
                                
symbols = t_env.sql_query("""              
                            SELECT 
                                 CAST(NULL  AS INT)      AS trader_id
                                ,CAST(NULL  AS INT)      AS login
                                ,CAST(NULL  AS INT)      AS trader_group_id
                                ,CAST(NULL AS STRING)    AS trader_group_name
                                ,symbol_id               AS symbol_id
                                ,name                    AS symbol_name
                                ,CAST('symbol' AS STRING)   AS src
                            FROM symbol
                        """)


# convert to streams
traders_ds = t_env.to_data_stream(traders)
trader_groups_ds = t_env.to_data_stream(trader_groups)
symbols_ds = t_env.to_data_stream(symbols)

# union_ds contains messages for trader, trader_group and symbol, column src shows the type of message
union_ds = traders_ds.union(trader_groups_ds).union(symbols_ds)
union_brdcst_messages_brdcast = union_ds.broadcast(union_brdcst_messages_state_descr)


# join positions with trader, trader_group and symbol
tbl_position =  t_env.from_path('position')
ds_positions = t_env.to_data_stream(tbl_position)


connected_stream = ds_positions.connect(union_brdcst_messages_brdcast)
ds_enriched_positions = connected_stream.process(BroadcastEnrichmentInfo(union_brdcst_messages_state_descr))


# keyed positions and orders and process them with a CoProcessFunction

ds_enriched_positions_keyed = ds_enriched_positions.key_by(lambda row: row['position_id'])

tbl_order =  t_env.from_path('order')
ds_orders_keyed = t_env.to_data_stream(tbl_order).key_by(lambda row: row[1])

ds_enriched_orders = ds_enriched_positions_keyed.connect(ds_orders_keyed).process(PositionsOrdersJoin())


# key orders and deals and process them with a CoProcessFunction
ds_enriched_orders_keyed = ds_enriched_orders.key_by(lambda row: row['order_id'])

tbl_deal =  t_env.from_path('deal')
ds_deals_keyed = t_env.to_data_stream(tbl_deal).key_by(lambda row: row[1])

ds_enriched_deals = ds_deals_keyed.connect(ds_enriched_orders_keyed).process(OrdersDealsJoin())


ds_enriched_deals.map(lambda x: logger.info(f"final_ds: {x}"))


env.execute("Convert Table to DataStream Example")