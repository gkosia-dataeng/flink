import logging
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.functions import CoProcessFunction
from pyflink.datastream.state import MapStateDescriptor
from pyflink.common.typeinfo import Types
from pyflink.table import StreamTableEnvironment

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



class OutputRecord:
    
    def __init__(self, id, totalProfit, create_date):
        self.id = id
        self.profit = totalProfit
        self.createdate = create_date

    def enrich_user_name(self, name):
        self.user_name = name

    def __str__(self):
        return f"OutputRecord(id = {self.id}, profit = {self.profit}, createdate = {self.createdate}, user_name = {self.user_name})"


class JoinTwoStreams(CoProcessFunction):

    def open(self, runtime_context):
        logger.info("JoinTwoStreams open called...Yes!!!")

        self.users_state = runtime_context.get_map_state(
            MapStateDescriptor("user_details", Types.LONG(), Types.STRING())
        )

    def process_element1(self, topicb, ctx):
        
        output = OutputRecord(topicb['user_id'], topicb['totalProfit'], topicb['create_date'])
        user_name = self.users_state.get(output.id)

        
        logger.info(f"Works!!! {user_name}")

        if user_name:
            output.enrich_user_name(user_name)
        else:
            output.enrich_user_name('USER_NAME_NOT_FOUND')
        

        return [output]
            
        
        

    def process_element2(self, topica, ctx):
        self.users_state.put(topica['user_id'], topica['name'])
        logger.info(f"Works!!! Storing in state {topica['name']}")




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

t_env.execute_sql("""CREATE TABLE position (
        position_id INT,
        symbol_id INT,
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

t_env.execute_sql("""CREATE TABLE order (
        order_id INT,
        position_Id INT,
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



table_a =  t_env.from_path('topica')
ds_topica = t_env.to_data_stream(table_a).key_by(lambda row: row[0])
table_b = t_env.from_path('topicb')
ds_topicb = t_env.to_data_stream(table_b).key_by(lambda row: row[0])



joined_stream = ds_topicb.connect(ds_topica).process(JoinTwoStreams())

joined_stream.map(lambda x: logger.info(f"Output of stream is {str(x)}"))

env.execute("Convert Table to DataStream Example")