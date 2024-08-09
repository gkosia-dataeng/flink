package gkosia.flink.java.models;


import java.time.Duration;
import java.util.Objects;


public class UserStatistics {
    public String emailAddress;
    public Duration totalFlightDuration;
    public long numberOfFlights;

    public UserStatistics() {
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        UserStatistics that = (UserStatistics) o;
        return numberOfFlights == that.numberOfFlights && Objects.equals(emailAddress, that.emailAddress) && Objects.equals(totalFlightDuration, that.totalFlightDuration);
    }

    @Override
    public int hashCode() {
        return Objects.hash(emailAddress, totalFlightDuration, numberOfFlights);
    }

    @Override
    public String toString() {
        return "UserStatistics{" +
                "emailAddress='" + emailAddress + '\'' +
                ", totalFlightDuration=" + totalFlightDuration +
                ", numberOfFlights=" + numberOfFlights +
                '}';
    }
    
}
