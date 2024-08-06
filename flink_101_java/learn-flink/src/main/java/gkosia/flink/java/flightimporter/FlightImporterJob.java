package gkosia.flink.java.flightimporter;


import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.api.common.serialization.SimpleStringSchema;
import org.apache.flink.connector.kafka.source.KafkaSource;
import org.apache.flink.connector.kafka.source.enumerator.initializer.OffsetsInitializer;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;

import java.io.InputStream;
import java.util.Properties;

import gkosia.flink.java.models.SkyOneAirlinesFlightData;
import org.apache.flink.formats.json.JsonDeserializationSchema;

public class FlightImporterJob {



    public static void main(String[] args) throws Exception{
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

        Properties consumerConfig = new Properties();
        try(InputStream stream = FlightImporterJob.class.getClassLoader().getResourceAsStream("consumer.properties")){
            consumerConfig.load(stream);
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

        stream.print();

        env.execute("FlightImporter");
    }
}
