package gkosia.flink.java.models;


import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.annotation.JsonFormat;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.annotation.JsonIgnoreProperties;

import java.time.ZonedDateTime;
import java.util.Objects;


@JsonIgnoreProperties(ignoreUnknown = true)
// POJO that will be used for serialization
public class SkyOneAirlinesFlightData {
    // POJO rule 2: all fields public or accessible from getters and setters
    public String emailAddress;
    @JsonFormat(shape = JsonFormat.Shape.STRING, pattern = "yyyy-MM-dd'T'HH:mm:ss.SSSXXX")
    public ZonedDateTime flightDepartureTime;
    public String iataDepartureCode ;
    @JsonFormat(shape = JsonFormat.Shape.STRING, pattern = "yyyy-MM-dd'T'HH:mm:ss.SSSXXX")
    public ZonedDateTime flightArrivalTime;
    public String iataArrivalCode;
    public String flightNumber;
    String confirmation; 


    // POJO rule 1: empty constructor
     public SkyOneAirlinesFlightData(){}
     
     public String getConfirmation(){
        return confirmation;
     }

     public void setConfirmation(String conf){
        confirmation = conf;
     }


    @Override
    public boolean equals(Object o) {
        if (this == o) return true; // if reference to the same instance
        if (o == null || getClass() != o.getClass()) return false; // is it is different Types
        SkyOneAirlinesFlightData that = (SkyOneAirlinesFlightData) o;
        return Objects.equals(emailAddress, that.emailAddress) && Objects.equals(flightDepartureTime, that.flightDepartureTime) && Objects.equals(iataDepartureCode, that.iataDepartureCode) && Objects.equals(flightArrivalTime, that.flightArrivalTime) && Objects.equals(iataArrivalCode, that.iataArrivalCode) && Objects.equals(flightNumber, that.flightNumber) && Objects.equals(confirmation, that.confirmation);
    }

    @Override
    public int hashCode() {
        return Objects.hash(emailAddress, flightDepartureTime, iataDepartureCode, flightArrivalTime, iataArrivalCode, flightNumber, confirmation);
    }

    @Override
    public String toString() {
        return "SkyOneAirlinesFlightData{" +
            "emailAddress='" + emailAddress + '\'' +
            ", flightDepartureTime=" + flightDepartureTime +
            ", iataDepartureCode='" + iataDepartureCode + '\'' +
            ", flightArrivalTime=" + flightArrivalTime +
            ", iataArrivalCode='" + iataArrivalCode + '\'' +
            ", flightNumber='" + flightNumber + '\'' +
            ", confirmation='" + confirmation + '\'' + 
            '}';
    }


    public FlightData toFlightData(){
        FlightData output  = new FlightData();

        output.emailAddress = emailAddress;
        output.departureTime = flightDepartureTime;
        output.departureAirportCode = iataDepartureCode;
        output.arrivalTime = flightArrivalTime;
        output.arrivalAirportCode = iataArrivalCode;
        output.flightNumber = flightNumber;
        output.confirmationCode = confirmation;

        return output;
    }

}

