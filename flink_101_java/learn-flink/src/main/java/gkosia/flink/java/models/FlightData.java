package gkosia.flink.java.models;

import java.time.ZonedDateTime;
import java.util.Objects;

import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.annotation.JsonFormat;

public class FlightData {
 public String emailAddress;
 @JsonFormat(shape = JsonFormat.Shape.STRING, pattern = "yyyy-MM-dd'T'HH:mm:ss.SSSXXX")
 public ZonedDateTime departureTime;
 public  String departureAirportCode;
 @JsonFormat(shape = JsonFormat.Shape.STRING, pattern = "yyyy-MM-dd'T'HH:mm:ss.SSSXXX")
 public ZonedDateTime arrivalTime;
 public  String arrivalAirportCode;
 public String flightNumber;
 public String confirmationCode;


 public FlightData(){}

 @Override
    public boolean equals(Object o) {
        if (this == o) return true; // if reference to the same instance
        if (o == null || getClass() != o.getClass()) return false; // is it is different Types
        FlightData that = (FlightData) o;
        return Objects.equals(emailAddress, that.emailAddress) && Objects.equals(departureTime, that.departureTime) && Objects.equals(departureAirportCode, that.departureAirportCode);
    }

    @Override
    public int hashCode() {
        return Objects.hash(emailAddress, departureTime,departureAirportCode, arrivalTime,arrivalAirportCode, flightNumber, confirmationCode);
    }

    @Override
    public String toString() {
        return "FlightData{" +
            "emailAddress='" + emailAddress + '\'' +
            ", departureTime=" + departureTime +
            ", departureAirportCode='" + departureAirportCode + '\'' +
            ", arrivalTime=" + arrivalTime +
            ", arrivalAirportCode='" + arrivalAirportCode + '\'' +
            ", flightNumber='" + flightNumber + '\'' +
            ", confirmationCode='" + confirmationCode + '\'' + 
            '}';
    }
}
