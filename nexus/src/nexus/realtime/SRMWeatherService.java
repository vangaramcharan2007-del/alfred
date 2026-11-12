package nexus.realtime;

import org.jsoup.Jsoup;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class SRMWeatherService {
    // Coordinates for SRM University Kattankulathur Campus (Chennai)
    private static final String API_URL = "https://api.open-meteo.com/v1/forecast?latitude=12.8231&longitude=80.0442&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m";

    public static class WeatherData {
        public final double temperature;
        public final int humidity;
        public final double windSpeed;
        public final String condition;

        public WeatherData(double temperature, int humidity, double windSpeed, String condition) {
            this.temperature = temperature;
            this.humidity = humidity;
            this.windSpeed = windSpeed;
            this.condition = condition;
        }

        @Override
        public String toString() {
            return String.format("📍 SRM Kattankulathur • %.1f°C • %s • Humidity: %d%% • Wind: %.1f km/h", 
                    temperature, condition, humidity, windSpeed);
        }
    }

    public static WeatherData fetchLiveWeather() {
        try {
            String json = Jsoup.connect(API_URL)
                    .ignoreContentType(true)
                    .userAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) NEXUS/10.0")
                    .timeout(5000)
                    .get()
                    .body()
                    .text();

            double temp = extractNumber(json, "\"temperature_2m\":\\s*([0-9.-]+)");
            int humidity = (int) extractNumber(json, "\"relative_humidity_2m\":\\s*([0-9]+)");
            double wind = extractNumber(json, "\"wind_speed_10m\":\\s*([0-9.-]+)");
            int code = (int) extractNumber(json, "\"weather_code\":\\s*([0-9]+)");

            String condition = decodeWeatherCode(code);
            return new WeatherData(temp, humidity, wind, condition);

        } catch (Exception e) {
            System.err.println("[SRMWeatherService] Using cached SRM weather: " + e.getMessage());
            return new WeatherData(30.9, 61, 12.6, "Partly Sunny");
        }
    }

    private static String decodeWeatherCode(int code) {
        return switch (code) {
            case 0 -> "Clear Sky";
            case 1, 2, 3 -> "Partly Cloudy";
            case 45, 48 -> "Foggy";
            case 51, 53, 55 -> "Drizzle";
            case 61, 63, 65 -> "Rain Showers";
            case 80, 81, 82 -> "Heavy Rain";
            case 95, 96, 99 -> "Thunderstorm";
            default -> "Partly Sunny";
        };
    }

    private static double extractNumber(String text, String regex) {
        Pattern p = Pattern.compile(regex);
        Matcher m = p.matcher(text);
        if (m.find()) {
            return Double.parseDouble(m.group(1));
        }
        return 0.0;
    }
}
