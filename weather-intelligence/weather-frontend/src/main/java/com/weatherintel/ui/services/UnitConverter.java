package com.weatherintel.ui.services;

import java.util.Locale;

/**
 * Utility class for converting weather units and formatting weather metrics.
 */
public final class UnitConverter {

    private static final String[] COMPASS_DIRECTIONS = {
            "N", "NE", "E", "SE", "S", "SW", "W", "NW"
    };

    private UnitConverter() {
        // Private constructor for utility class
    }

    public static double celsiusToFahrenheit(double c) {
        return (c * 9.0 / 5.0) + 32.0;
    }

    public static double fahrenheitToCelsius(double f) {
        return (f - 32.0) * 5.0 / 9.0;
    }

    public static double msToKmh(double ms) {
        return ms * 3.6;
    }

    public static double msToMph(double ms) {
        return ms * 2.23693629;
    }

    public static double msToKnots(double ms) {
        return ms * 1.94384449;
    }

    public static double hPaToMmHg(double hpa) {
        return hpa * 0.75006157584566;
    }

    public static double metersToMiles(double m) {
        return m * 0.000621371192;
    }

    public static String degreesToDirection(int degrees) {
        int normalized = ((degrees % 360) + 360) % 360;
        int index = (int) Math.round(normalized / 45.0) % 8;
        return COMPASS_DIRECTIONS[index];
    }

    public static String formatTemperature(double temp, boolean celsius) {
        double val = celsius ? temp : celsiusToFahrenheit(temp);
        return String.format(Locale.US, "%.1f°%s", val, celsius ? "C" : "F");
    }

    public static String formatWindSpeed(double speed, String unit) {
        if (unit == null || unit.isBlank()) {
            unit = "km/h";
        }
        double converted;
        String displayUnit;
        switch (unit.toLowerCase(Locale.ROOT).trim()) {
            case "mph" -> {
                converted = msToMph(speed);
                displayUnit = "mph";
            }
            case "knots", "knot", "kt" -> {
                converted = msToKnots(speed);
                displayUnit = "knots";
            }
            case "m/s", "ms" -> {
                converted = speed;
                displayUnit = "m/s";
            }
            case "km/h", "kmh" -> {
                converted = msToKmh(speed);
                displayUnit = "km/h";
            }
            default -> {
                converted = msToKmh(speed);
                displayUnit = unit;
            }
        }
        return String.format(Locale.US, "%.1f %s", converted, displayUnit);
    }
}
