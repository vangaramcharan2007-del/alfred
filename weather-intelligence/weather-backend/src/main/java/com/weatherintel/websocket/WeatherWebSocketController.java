package com.weatherintel.websocket;

import com.weatherintel.dto.WeatherResponse;
import com.weatherintel.service.WeatherService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.messaging.handler.annotation.MessageMapping;
import org.springframework.messaging.handler.annotation.SendTo;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Controller;

@Controller
public class WeatherWebSocketController {

    private static final Logger log = LoggerFactory.getLogger(WeatherWebSocketController.class);

    private final SimpMessagingTemplate messagingTemplate;
    private final WeatherService weatherService;

    public WeatherWebSocketController(SimpMessagingTemplate messagingTemplate, WeatherService weatherService) {
        this.messagingTemplate = messagingTemplate;
        this.weatherService = weatherService;
    }

    @MessageMapping("/weather/subscribe")
    @SendTo("/topic/weather/updates")
    public WeatherResponse handleSubscribe(String cityName) {
        log.info("Client subscribed to weather updates for city: {}", cityName);
        return weatherService.getCurrentWeather(cityName);
    }

    public void broadcastWeatherUpdate(Long cityId, WeatherResponse weatherResponse) {
        log.debug("Broadcasting weather update for cityId: {}", cityId);
        messagingTemplate.convertAndSend("/topic/weather/" + cityId, weatherResponse);
        messagingTemplate.convertAndSend("/topic/weather/updates", weatherResponse);
    }
}
