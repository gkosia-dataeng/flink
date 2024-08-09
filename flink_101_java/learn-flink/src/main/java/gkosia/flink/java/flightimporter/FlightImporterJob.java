package gkosia.flink.java.flightimporter;
//gkosia.flink.java.flightimporter.FlightImporterJob

import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.connector.kafka.source.KafkaSource;
import org.apache.flink.connector.kafka.source.enumerator.initializer.OffsetsInitializer;
import org.apache.flink.streaming.api.datastream.ConnectedStreams;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.co.CoMapFunction;
import java.io.InputStream;
import java.time.ZonedDateTime;
import java.util.Properties;

import gkosia.flink.java.models.FlightData;
import gkosia.flink.java.models.SunsetAirlinesFlightData;
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
        

        /*
         * 
         *  SkyOneAirlinesFlightData: read the SkyOne source messages
         * 
         */
        KafkaSource<SkyOneAirlinesFlightData> ksource_skyone = KafkaSource.<SkyOneAirlinesFlightData>builder()
        .setProperties(consumerConfig)
        .setTopics("skyone")
        .setStartingOffsets(OffsetsInitializer.latest())
        .setValueOnlyDeserializer(new JsonDeserializationSchema(SkyOneAirlinesFlightData.class))
        .build();
        

        DataStream<SkyOneAirlinesFlightData> stream_skyone = env.fromSource(
         ksource_skyone  
        ,WatermarkStrategy.noWatermarks()
        ,"skyone_source");
        

        /*
         * 
         *  SunsetAirlinesFlightData: read the Sunset source messages
         * 
         */
        KafkaSource<SunsetAirlinesFlightData> ksource_sunset = KafkaSource.<SunsetAirlinesFlightData>builder()
        .setProperties(consumerConfig)
        .setTopics("sunset")
        .setStartingOffsets(OffsetsInitializer.latest())
        .setValueOnlyDeserializer(new JsonDeserializationSchema(SunsetAirlinesFlightData.class))
        .build();
        

        DataStream<SunsetAirlinesFlightData> stream_sunset = env.fromSource(
            ksource_sunset  
        ,WatermarkStrategy.noWatermarks()
        ,"sunset_source");



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


        defineWorkflow(stream_skyone, stream_sunset)
        .sinkTo(sink)
        .name("sink_data");

        env.execute("FlightImporter");
    }


    public static DataStream<FlightData> defineWorkflow(DataStream<SkyOneAirlinesFlightData> skyOneSource, DataStream<SunsetAirlinesFlightData> sunsetSource ){
        
        // use the union
        // map each stream to the common Type and then Union them
        /*

        DataStream<FlightData> output_skyone, output_sunset;

         
            output_skyone = skyOneSource
                    .filter(flight -> flight.flightArrivalTime.isAfter(ZonedDateTime.now()))
                    .map(SkyOneAirlinesFlightData::toFlightData);

            output_sunset = sunsetSource
                            .filter(flight -> flight.arrivalTime.isAfter(ZonedDateTime.now()))
                            .map(SunsetAirlinesFlightData::toFlightData);


            
            return output_skyone.union(output_sunset);

        */
        // use the connect
        // Connect the stream and then apply a CoMap function to Mapo them to the new Type
        DataStream<SkyOneAirlinesFlightData> output_skyone = skyOneSource
                    .filter(flight -> flight.flightArrivalTime.isAfter(ZonedDateTime.now()));

        DataStream<SunsetAirlinesFlightData> output_sunset = sunsetSource
                    .filter(flight -> flight.arrivalTime.isAfter(ZonedDateTime.now()));
                                                 
        DataStream<FlightData> stream = output_skyone.
                                        connect(output_sunset).
                                        map(new CoMapFunction<SkyOneAirlinesFlightData,SunsetAirlinesFlightData,FlightData>(){
                                                    @Override
                                                    public FlightData map1(SkyOneAirlinesFlightData f){
                                                        return f.toFlightData();
                                                    }

                                                    @Override
                                                    public FlightData map2(SunsetAirlinesFlightData f){
                                                        return f.toFlightData();
                                                    }
                                                 });

        return stream;
    }
}
