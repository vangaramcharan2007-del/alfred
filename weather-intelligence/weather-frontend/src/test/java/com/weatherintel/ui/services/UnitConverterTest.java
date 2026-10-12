package com.weatherintel.ui.services;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class UnitConverterTest {

    @Test
    @DisplayName("Should convert Celsius to Fahrenheit and vice versa accurately")
    void testTemperatureConversions() {
        assertEquals(32.0, UnitConverter.celsiusToFahrenheit(0.0), 0.01);
        assertEquals(212.0, UnitConverter.celsiusToFahrenheit(100.0), 0.01);
        assertEquals(-40.0, UnitConverter.celsiusToFahrenheit(-40.0), 0.01);

        assertEquals(0.0, UnitConverter.fahrenheitToCelsius(32.0), 0.01);
        assertEquals(100.0, UnitConverter.fahrenheitToCelsius(212.0), 0.01);
        assertEquals(-40.0, UnitConverter.fahrenheitToCelsius(-40.0), 0.01);
    }

    @Test
    @DisplayName("Should convert wind speeds correctly across units")
    void testWindSpeedConversions() {
        // 10 m/s = 36 km/h
        assertEquals(36.0, UnitConverter.msToKmh(10.0), 0.01);

        // 10 m/s ~ 22.37 mph
        assertEquals(22.37, UnitConverter.msToMph(10.0), 0.05);

        // 10 m/s ~ 19.44 knots
        assertEquals(19.44, UnitConverter.msToKnots(10.0), 0.05);
    }

    @Test
    @DisplayName("Should convert pressure from hPa to mmHg")
    void testPressureConversions() {
        // 1013.25 hPa ~ 760 mmHg
        assertEquals(760.0, UnitConverter.hPaToMmHg(1013.25), 0.1);
    }

    @Test
    @DisplayName("Should map degree angles to correct compass cardinal directions")
    void testDegreesToDirection() {
        assertEquals("N", UnitConverter.degreesToDirection(0));
        assertEquals("N", UnitConverter.degreesToDirection(360));
        assertEquals("NE", UnitConverter.degreesToDirection(45));
        assertEquals("E", UnitConverter.degreesToDirection(90));
        assertEquals("SE", UnitConverter.degreesToDirection(135));
        assertEquals("S", UnitConverter.degreesToDirection(180));
        assertEquals("SW", UnitConverter.degreesToDirection(225));
        assertEquals("W", UnitConverter.degreesToDirection(270));
        assertEquals("NW", UnitConverter.degreesToDirection(315));
    }
}
