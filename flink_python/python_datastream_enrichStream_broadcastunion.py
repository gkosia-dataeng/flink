from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment
import logging
from pyflink.datastream.functions import BroadcastProcessFunction, CoProcessFunction
from pyflink.datastream.state import MapStateDescriptor
from pyflink.common.typeinfo import Types
from datetime import timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)




union_brdcst_messages_state_descr = MapStateDescriptor("union_brdcst_messages", Types.STRING(), Types.TUPLE([Types.LONG(),Types.LONG(),Types.LONG(), Types.STRING(), Types.LONG(), Types.STRING(), Types.STRING()]))
position_descr = MapStateDescriptor("position", Types.LONG(), Types.TUPLE( [Types.STRING(), Types.LONG()]))
order_descr = MapStateDescriptor("order",   Types.LONG(), Types.TUPLE([Types.LONG(), Types.STRING(), Types.SQL_TIMESTAMP()]) )
order_enriched_descr =MapStateDescriptor("order_enriched", Types.LONG(), Types.TUPLE([Types.LONG(), Types.STRING(), Types.LONG(), Types.STRING()]) )
deal_descr = MapStateDescriptor("deal", Types.LONG(), Types.TUPLE([Types.LONG(), Types.DOUBLE(), Types.SQL_TIMESTAMP(), Types.SQL_TIMESTAMP()]) )

class BroadcastEnrichmentInfo(BroadcastProcessFunction):

    def __init__(self, union_brdcst_messages_state_descr):
        self.union_brdcst_messages_state_descr = union_brdcst_messages_state_descr

    # trader or symbol or trader group
    def process_broadcast_element(self, data, ctx):
        logger.info(f"joiner - process_broadcast_element: {data}")

        state = ctx.get_broadcast_state(self.union_brdcst_messages_state_descr)

        if data['src'] == 'trader':
            key =  "t_" + str(data['trader_id'])
        elif data['src'] == 'trader_group':
            key =  "tg_" + str(data['trader_group_id'])
        elif data['src'] == 'symbol':
            key =  "s_" + str(data['symbol_id'])
        else:
            key = None
            logger.info(f"joiner - process_broadcast_element - BroadcastEnrichmentInfo: Received {data} but not matched with a type")
        
        # replace None values because is trying to encode and cannot encode None  
        if key:
            state_value  = (
                  data['trader_id'] if data['trader_id'] is not None else -99
                ,data['login']  if data['login'] is not None else -99
                ,data['trader_group_id']  if data['trader_group_id'] is not None else -99
                ,data['trader_group_name']  if data['trader_group_name'] is not None else ""
                ,data['symbol_id']  if data['symbol_id'] is not None else -99
                ,data['symbol_name']  if data['symbol_name'] is not None else ""
                ,data['src']
            )

            state.put(key, state_value)
            logger.info(f"joiner - process_broadcast_element - BroadcastEnrichmentInfo: stored broadcasted object in state with key {key}")


    def process_element(self, position, ctx):
        
        logger.info(f"joiner - process_element - BroadcastEnrichmentInfo: {str(position)}")
        symbol_id = "s_" + str(position[1])
        trader_id = "t_" + str(position[2])
        

        enriched_position = {
                    "position_id": position['position_id']
        }


        state = ctx.get_broadcast_state(self.union_brdcst_messages_state_descr)

        # enrich from symbol
        symbol = state.get(symbol_id)
        trader = state.get(trader_id)


        if symbol and trader:
            enriched_position["symbol"] = symbol[5]
            enriched_position["login"] = trader[1]

            logger.info(f"joiner - process_element - BroadcastEnrichmentInfo: Successfully enriched position {enriched_position}")
            return [enriched_position]
        else:
            logger.info(f"joiner - process_element - BroadcastEnrichmentInfo: Missing enrichment info for position {enriched_position}")
                
        
        

class PositionsOrdersJoin(CoProcessFunction):

    def open(self, runtime_context):
        self.orders_state = runtime_context.get_map_state(order_descr)
        self.positions_state = runtime_context.get_map_state(position_descr)

    def process_element1(self, position, ctx):

        # one position can have many orders, so store the postion in state
        self.positions_state.put(position['position_id'], (position['symbol'], position['login']))

        order = self.orders_state.get(position['position_id'])

        if order:
            position['order_id'] = order[0]
            position['type'] = order[1]
            position['update_time'] = order[2]
            logger.info(f"joiner - process_element1 - PositionsOrdersJoin : Position match with order: {position}")
            self.orders_state.remove(position['position_id'])
            return [position]

    def process_element2(self, order, ctx):

        position = self.positions_state.get(order['position_id'])

        if position:
            position_enriched = {
                 "position_id": order['position_id']
                ,"symbol": position[0]
                ,"login": position[1]
                ,"order_id": order['order_id']
                ,"type": order['type']
                ,"update_time": order['update_time']
            }

            logger.info(f"joiner - process_element2 - PositionsOrdersJoin : Order enriched from position: {order}")
            return [position_enriched]
        else:
            self.orders_state.put(order['position_id'], (order['order_id'], order['type'],order['update_time']))
            logger.info(f"joiner - process_element2 - PositionsOrdersJoin : Position not found, order stored in state: {order}")


class OrdersDealsJoin(CoProcessFunction):
    
    def open(self, runtime_context):
        self.orders_state = runtime_context.get_map_state(order_enriched_descr)
        self.deal_state =  runtime_context.get_map_state(deal_descr)
    
    
    def process_element1(self, deal, ctx):
        order = self.orders_state.get(deal['order_id'])


        if order:

            msg = {
                 "deal_id": deal['deal_id']
                ,"order_id": deal['order_id']
                ,"position_id": order[0]
                ,"symbol": order[1]
                ,"login": order[2]
                ,"type": order[3]
                ,"profit": deal['profit']
                ,"create_date": deal['create_date']
                ,"update_time": deal['update_time']
            }

            logger.info(f"joiner - process_element1 -  OrdersDealsJoin: Deal enriched {msg}")
            self.orders_state.remove(deal['order_id'])
            return [msg]
        else:
            self.deal_state.put(deal['order_id'], (deal['deal_id'], deal['profit'], deal['create_date'], deal['update_time']))
            logger.info(f"joiner - process_element1 -  OrdersDealsJoin: Order not found, deal stored in state {deal['deal_id']}")


    def process_element2(self, order, ctx):
        
        deal = self.deal_state.get(order['order_id'])

        if deal:

            msg = {
                 "deal_id": deal[0]
                ,"order_id": order['order_id']
                ,"position_id": order['position_id']
                ,"symbol": order['symbol']
                ,"login": order['login']
                ,"type":  order['type']
                ,"profit": deal[1]
                ,"create_date": deal[2]
                ,"update_time": deal[3]
            }

            self.deal_state.remove(order['order_id'])
            logger.info(f"joiner - process_element2 -  OrdersDealsJoin: Deal enriched {msg}")
            return  [msg]
        else:
            self.orders_state.put(order['order_id'], (order['position_id'], order['symbol'],order['login'], order['type']))
            logger.info(f"joiner - process_element2 -  OrdersDealsJoin: Deal not found, order stored in state {order}")
            event_time = order['update_time']
            ctx.timer_service().register_event_time_timer((event_time + timedelta(minutes=10)).timestamp() * 1000) # drop order after 10 mins if deal dont come

    def on_timer(self, timestamp, ctx):
        logger.info(f"joiner - on_timer - OrdersDealsJoin: timer fired, cleaning order from state")
        self.orders_state.clear() # clear the record of specific key from the state






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


ds_enriched_deals.map(lambda x: logger.info(f"joiner - final_ds: {x}"))


env.execute("Convert Table to DataStream Example")