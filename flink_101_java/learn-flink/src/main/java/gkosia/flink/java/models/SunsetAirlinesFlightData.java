package gkosia.flink.java.models;

import java.time.ZonedDateTime;
import java.util.Objects;

import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.annotation.JsonFormat;

import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.annotation.JsonIgnoreProperties;

@JsonIgnoreProperties(ignoreUnknown = true)
public class SunsetAirlinesFlightData {
    public String customerEmailAddress;
    @JsonFormat(shape = JsonFormat.Shape.STRING, pattern = "yyyy-MM-dd'T'HH:mm:ss.SSSXXX")
    public ZonedDateTime departureTime;
    public String departureAirport;
    @JsonFormat(shape = JsonFormat.Shape.STRING, pattern = "yyyy-MM-dd'T'HH:mm:ss.SSSXXX")
    public ZonedDateTime arrivalTime;
    public String arrivalAirport;
    public String flightId;
    public String referenceNumber;


    @Override
    public boolean equals(Object o) {
        if (this == o) return true; // if reference to the same instance
        if (o == null || getClass() != o.getClass()) return false; // is it is different Types
        SunsetAirlinesFlightData that = (SunsetAirlinesFlightData) o;
        return Objects.equals(customerEmailAddress, that.customerEmailAddress) && Objects.equals(departureTime, that.departureTime) && Objects.equals(departureAirport, that.departureAirport);
    }

    @Override
    public int hashCode() {
        return Objects.hash(customerEmailAddress, departureTime, departureAirport, arrivalTime, arrivalAirport, flightId, referenceNumber);
    }

    @Override
    public String toString() {
        return "SunsetAirlinesFlightData{" +
            "customerEmailAddress='" + customerEmailAddress + '\'' +
            ", departureTime=" + departureTime +
            ", departureAirport=" + departureAirport +
            ", arrivalTime='" + arrivalTime + '\'' +
            ", arrivalAirport='" + arrivalAirport + '\'' +
            ", flightId='" + flightId + '\'' +
            ", referenceNumber='" + referenceNumber + '\'' + 
            '}';
    }


    public FlightData toFlightData(){
        FlightData output  = new FlightData();

        output.emailAddress = customerEmailAddress;
        output.departureTime = departureTime;
        output.departureAirportCode = departureAirport;
        output.arrivalTime = arrivalTime;
        output.arrivalAirportCode = arrivalAirport;
        output.flightNumber = flightId;
        output.confirmationCode = referenceNumber;

        return output;
    }
}

