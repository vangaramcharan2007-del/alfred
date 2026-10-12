package com.weatherintel;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication
@EnableScheduling
public class WeatherIntelApplication {

    public static void main(String[] args) {
        SpringApplication.run(WeatherIntelApplication.class, args);
    }
}
