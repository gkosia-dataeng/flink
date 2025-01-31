from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.typeinfo import Types
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaSink, KafkaRecordSerializationSchema, DeliveryGuarantee, KafkaOffsetsInitializer
from pyflink.datastream.functions import MapFunction
from pyflink.common.watermark_strategy import WatermarkStrategy
from pyflink.datastream.execution_mode import RuntimeExecutionMode
import json


# Implement the custom Deserialization logic.
class DebeziumDeserializationSchema(MapFunction):
    def map(self, value):
        event = json.loads(value)
        # Do further processing or return transformed event
        if event['after']['profit'] > 1000:
            event['after']['deal_profit_level'] = 'high'
        else:
            event['after']['deal_profit_level'] = 'low'

        
        
        return json.dumps(event['after'])
        

def start_the_stream():
  
    # Declare the execution environment.
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)
    env.set_runtime_mode(RuntimeExecutionMode.STREAMING)

    # Deals source
    source = KafkaSource.builder() \
        .set_bootstrap_servers("kafka:19092") \
        .set_topics("source_postgresql.public.deals") \
        .set_group_id("datastream_api") \
        .set_starting_offsets(KafkaOffsetsInitializer.earliest()) \
        .set_value_only_deserializer(SimpleStringSchema()) \
        .build()
    
    ds = env.from_source(source, WatermarkStrategy.for_monotonous_timestamps(), "Kafka Source")

    

    # Apply the map function to process each post.
    stream = ds.map(DebeziumDeserializationSchema(), output_type=Types.STRING())

    # Define a sink to write to Kafka.
    sink = KafkaSink.builder() \
        .set_bootstrap_servers("kafka:19092") \
        .set_record_serializer(
            KafkaRecordSerializationSchema.builder()
                .set_topic("deals-enriched")
                .set_value_serialization_schema(SimpleStringSchema())
                .build()
        ) \
        .set_delivery_guarantee(DeliveryGuarantee.AT_LEAST_ONCE) \
        .build()

    # Direct the processed data to the sink.
    stream.sink_to(sink)

    # Execute the job.
    env.execute()

if __name__ == "__main__":
    start_the_stream()