import logging
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.functions import BroadcastProcessFunction, CoProcessFunction
from pyflink.datastream.state import MapStateDescriptor
from pyflink.common.typeinfo import Types
from pyflink.table import StreamTableEnvironment
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



class BroadcastEnrichmentInfo(BroadcastProcessFunction):

    def __init__(self, symbols_descr, groups_descr, traders_descr):
        self.symbols_state_descr = symbols_descr
        self.groups_state_descr  = groups_descr
        self.traders_state_descr = traders_descr

        
    def process_broadcast_element(self, value, ctx):
        data = value
        logger.info(f"process_broadcast_element: {data}")

        if hasattr(data, 'trader_id'):
            brd_state = ctx.get_broadcast_state(self.traders_state_descr)
            brd_state.put(data['trader_id'], {"trader_group_id": str(data['trader_group_id'])})
            logger.info(f" process_broadcast_element Broadcast message trader, storing {data['trader_id']} and group {data['trader_group_id']}")
        elif hasattr(data, 'trader_group_id'):
            brd_state = ctx.get_broadcast_state(self.groups_state_descr)
            brd_state.put(data['trader_group_id'], {"group_name" : data['trader_group_name']})
            logger.info(f" process_broadcast_element Broadcast message trader group, storing {data['trader_group_id']} and group {data['trader_group_name']}")
        elif hasattr(data, 'symbol_id'):
            brd_state = ctx.get_broadcast_state(self.symbols_state_descr)
            brd_state.put(data['symbol_id'], {"name" : data['name']})
            logger.info(f" process_broadcast_element Broadcast message symbol, storing {data['symbol_id']} and group {data['name']}")
        else:
            logger.info(f"process_broadcast_element: Received {data} but not store it in state")


    def process_element(self, value, ctx):
        position = value
        logger.info(f"process_element: {str(position)}")
        symbol_id = position['symbol_id']
        trader_id = position['trader_id']


        logger.info(f"process_element symbol_id: {symbol_id}, trader_id: {trader_id}")
        
        symbols_state = ctx.get_broadcast_state(self.symbols_state_descr)
        symbol = symbols_state.get(symbol_id)


        if symbol:
            
            enriched_position = {
                'position_id': position['position_id']
                ,'symbol': symbol['name']
            }

            traders_state = ctx.get_broadcast_state(self.traders_state_descr)
            trader = traders_state.get(trader_id)

            if trader:
                enriched_position['login'] = trader['login']

            return [enriched_position]

        

        '''
        

        

        group_id = trader['trader_group_id']
        groups_state = ctx.get_broadcast_state(self.groups_state_descr)
        group = groups_state.get(group_id)
    

        logger.info(f"Got {position['position_id']}")
        


        
        '''
        
            


env = StreamExecutionEnvironment.get_execution_environment()
t_env = StreamTableEnvironment.create(env)


t_env.execute_sql("""CREATE TABLE symbol (
        symbol_id INT,
        name STRING,
        update_time TIMESTAMP(3),
        WATERMARK FOR update_time AS update_time - INTERVAL '5' SECOND
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
        WATERMARK FOR update_time AS update_time - INTERVAL '5' SECOND
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
        WATERMARK FOR update_time AS update_time - INTERVAL '5' SECOND
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
        WATERMARK FOR update_time AS update_time - INTERVAL '5' SECOND
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
        WATERMARK FOR update_time AS update_time - INTERVAL '5' SECOND
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
        WATERMARK FOR update_time AS update_time - INTERVAL '5' SECOND
    ) WITH (
        'connector' = 'kafka',
        'topic' = 'source-trader-group',
        'properties.bootstrap.servers' = 'kafka:19092',
        'value.format' = 'json',
        'properties.group.id' = 'test-group',
        'scan.startup.mode' = 'earliest-offset'
    )
    """)



tbl_symbol =  t_env.from_path('symbol')
ds_symbol = t_env.to_data_stream(tbl_symbol)
symbols_descr = MapStateDescriptor("symbols", Types.LONG(), Types.MAP(Types.STRING(), Types.STRING()))
ds_symbol_brdcast = ds_symbol.broadcast(symbols_descr)

tbl_trader_group =  t_env.from_path('trader_group')
ds_groups = t_env.to_data_stream(tbl_trader_group)
groups_descr = MapStateDescriptor("groups", Types.LONG(), Types.MAP(Types.STRING(), Types.STRING()))
ds_groups_brdcast = ds_groups.broadcast(groups_descr)


tbl_trader =  t_env.from_path('trader')
ds_traders = t_env.to_data_stream(tbl_trader)
traders_descr = MapStateDescriptor("traders", Types.LONG(), Types.MAP(Types.STRING(), Types.STRING()))
ds_traders_brdcast = ds_traders.broadcast(traders_descr)


tbl_position =  t_env.from_path('position')
ds_positions = t_env.to_data_stream(tbl_position)


symbol_connected_stream = ds_positions.connect(ds_symbol_brdcast)
login_connected_stream = symbol_connected_stream.connect(ds_traders_brdcast)
ds_enriched_positions = login_connected_stream.process(BroadcastEnrichmentInfo(symbols_descr, groups_descr, traders_descr))

'''
tbl_order =  t_env.from_path('order')
tbl_deal =  t_env.from_path('deal')

'''



ds_enriched_positions.map(lambda x: logger.info(f"ds_enriched_positions: {x}"))

env.execute("Convert Table to DataStream Example")