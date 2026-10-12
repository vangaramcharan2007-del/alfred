package com.weatherintel.exception;

public class WeatherApiException extends RuntimeException {
    private final int statusCode;

    public WeatherApiException(String message) {
        super(message);
        this.statusCode = 502;
    }

    public WeatherApiException(String message, int statusCode) {
        super(message);
        this.statusCode = statusCode;
    }

    public WeatherApiException(String message, Throwable cause, int statusCode) {
        super(message, cause);
        this.statusCode = statusCode;
    }

    public int getStatusCode() {
        return statusCode;
    }
}
