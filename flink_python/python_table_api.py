import sys
from pyflink.table import EnvironmentSettings, TableEnvironment, DataTypes, Schema, FormatDescriptor, TableDescriptor

def start_the_steam():

    # Initialize the Table Environment
    env_settings = EnvironmentSettings.in_streaming_mode()
    t_env = TableEnvironment.create(env_settings)

    # Define the kafka deals source
    t_env.create_temporary_table(
        'deals_source',
        TableDescriptor.for_connector('kafka')
            .schema(Schema.new_builder()
                    .column('deal_id', DataTypes.INT())
                    .column('platform_position_id', DataTypes.INT())
                    .column('login', DataTypes.INT())
                    .column('server', DataTypes.STRING())
                    .column('execution_time', DataTypes.BIGINT())
                    .column('position_impact', DataTypes.INT()) 
                    .column('trade_direction', DataTypes.INT()) 
                    .column('volumn', DataTypes.INT()) 
                    .column('profit', DataTypes.INT()) 
                    .build())
            .option('topic', 'source_postgresql.public.deals')
            .option('properties.bootstrap.servers', 'kafka:19092')
            .option('properties.group.id', 'pyflink_table_api')
            .option('scan.startup.mode', 'earliest-offset')
            .format(FormatDescriptor.for_format('debezium-json')
                    .build())
            .build())


    # Define the kafka deals source
    t_env.create_temporary_table(
        'accounts_source',
        TableDescriptor.for_connector('kafka')
            .schema(Schema.new_builder()
                    .column('login', DataTypes.INT())
                    .column('login_group', DataTypes.STRING())
                    .column('user_id', DataTypes.INT())
                    .build())
            .option('topic', 'source_postgresql.public.mt4account')
            .option('properties.bootstrap.servers', 'kafka:19092')
            .option('properties.group.id', 'pyflink_table_api')
            .option('scan.startup.mode', 'earliest-offset')
            .format(FormatDescriptor.for_format('debezium-json')
                    .build())
            .build())
    

    # Define the Kafka Sink Table
    t_env.execute_sql("""CREATE TABLE users_profit (
        user_id INT,
        totalProfit INT,
        PRIMARY KEY (user_id) NOT ENFORCED
    ) WITH (
        'connector' = 'upsert-kafka',
        'topic' = 'user-profit',
        'properties.bootstrap.servers' = 'kafka:19092',
        'key.format' = 'json',
        'value.format' = 'json'
    )
    """)
    
    t_env.execute_sql("""
        INSERT INTO users_profit
        SELECT a.user_id, SUM(d.profit)
        FROM accounts_source a
        LEFT JOIN deals_source d
          ON a.login = d.login
        GROUP BY a.user_id
    """)

if __name__ == '__main__':
    
    start_the_steam()