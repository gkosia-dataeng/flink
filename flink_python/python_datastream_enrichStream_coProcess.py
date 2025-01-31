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






t_env.execute_sql("""CREATE TABLE topica (
        user_id INT,
        name STRING,
        update_time TIMESTAMP(3),
        WATERMARK FOR update_time AS update_time - INTERVAL '5' SECOND
    ) WITH (
        'connector' = 'kafka',
        'topic' = 'test-source-atopic',
        'properties.bootstrap.servers' = 'kafka:19092',
        'value.format' = 'json',
        'properties.group.id' = 'test-group',
        'scan.startup.mode' = 'earliest-offset'
    )
    """)



t_env.execute_sql("""CREATE TABLE topicb (
        user_id INT,
        totalProfit DOUBLE,
        create_date TIMESTAMP(3),
        WATERMARK for create_date AS create_date - INTERVAL '5' SECOND
                      
    ) WITH (
        'connector' = 'kafka',
        'topic' = 'test-source-btopic',
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