package gkosia.flink.java.flightimporter;
//gkosia.flink.java.flightimporter.FlightImporterJob

import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.connector.kafka.source.KafkaSource;
import org.apache.flink.connector.kafka.source.enumerator.initializer.OffsetsInitializer;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;

import java.io.InputStream;
import java.time.ZonedDateTime;
import java.util.Properties;

import gkosia.flink.java.models.FlightData;
import gkosia.flink.java.models.SkyOneAirlinesFlightData;
import org.apache.flink.formats.json.JsonDeserializationSchema;


import org.apache.flink.connector.kafka.sink.KafkaRecordSerializationSchema;
import org.apache.flink.connector.kafka.sink.KafkaSink;   
import org.apache.flink.formats.json.JsonSerializationSchema;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;


public class FlightImporterJob {



    public static void main(String[] args) throws Exception{
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

        Properties consumerConfig = new Properties();
        Properties producerConfig = new Properties();
        try(
            InputStream cons_stream = FlightImporterJob.class.getClassLoader().getResourceAsStream("consumer.properties");
            InputStream prod_stream = FlightImporterJob.class.getClassLoader().getResourceAsStream("producer.properties");
            ){
            consumerConfig.load(cons_stream);
            producerConfig.load(prod_stream);
        }catch (Exception e) {
            System.out.println("Failed to load consumer properties");
            e.printStackTrace();
        }

        KafkaSource<SkyOneAirlinesFlightData> ksource = KafkaSource.<SkyOneAirlinesFlightData>builder()
        .setProperties(consumerConfig)
        .setTopics("skyone")
        .setStartingOffsets(OffsetsInitializer.latest())
        .setValueOnlyDeserializer(new JsonDeserializationSchema(SkyOneAirlinesFlightData.class))
        .build();
        

        DataStream<SkyOneAirlinesFlightData> stream = env.fromSource(
         ksource  
        ,WatermarkStrategy.noWatermarks()
        ,"skyone_source");


        KafkaRecordSerializationSchema<FlightData> serializer =  KafkaRecordSerializationSchema.<FlightData>builder()
        .setTopic("flightdata")
        .setValueSerializationSchema(new JsonSerializationSchema<FlightData>( 
            () -> {
            return new ObjectMapper().registerModule(new JavaTimeModule());
            }
        ))
        .build();

        
        KafkaSink<FlightData> sink = KafkaSink.<FlightData>builder()
        .setKafkaProducerConfig(producerConfig)
        .setRecordSerializer(serializer)
        .build();


        defineWorkflow(stream)
        .sinkTo(sink)
        .name("sink_data");

        env.execute("FlightImporter");
    }


    public static DataStream<FlightData> defineWorkflow(DataStream<SkyOneAirlinesFlightData> skyOneSource ){
        
        DataStream<FlightData> outputStream;

        outputStream = skyOneSource
                .filter(flight -> flight.flightArrivalTime.isAfter(ZonedDateTime.now()))
                .map(SkyOneAirlinesFlightData::toFlightData);

        return outputStream;
    }
}
