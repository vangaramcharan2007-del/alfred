package com.weatherintel.ui.services;

import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import org.java_websocket.handshake.ServerHandshake;

import javax.swing.*;
import java.net.URI;
import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * WebSocket client supporting STOMP messaging over WebSocket with auto-reconnection.
 * Connects to ws://localhost:8080/ws (or /ws/websocket) and subscribes to /topic/weather/updates.
 */
public class WebSocketClient {

    public interface WeatherUpdateListener {
        void onWeatherUpdate(ApiClient.WeatherData weatherData);
    }

    public interface ConnectionStatusListener {
        void onConnectionStatusChanged(boolean connected);
    }

    private static final String DEFAULT_WS_URL = "ws://localhost:8080/ws/websocket";
    private static final String TOPIC_WEATHER_UPDATES = "/topic/weather/updates";

    private final URI serverUri;
    private final ObjectMapper objectMapper;
    private final List<WeatherUpdateListener> weatherListeners = new CopyOnWriteArrayList<>();
    private final List<ConnectionStatusListener> connectionListeners = new CopyOnWriteArrayList<>();

    private org.java_websocket.client.WebSocketClient internalClient;
    private final ScheduledExecutorService reconnectExecutor = Executors.newSingleThreadScheduledExecutor(r -> {
        Thread t = new Thread(r, "WebSocket-Reconnect-Thread");
        t.setDaemon(true);
        return t;
    });

    private final AtomicBoolean isRunning = new AtomicBoolean(false);
    private final AtomicBoolean isConnected = new AtomicBoolean(false);
    private final AtomicBoolean isReconnecting = new AtomicBoolean(false);

    public WebSocketClient() {
        this(DEFAULT_WS_URL);
    }

    public WebSocketClient(String wsUrl) {
        if (wsUrl == null || wsUrl.isBlank()) {
            wsUrl = DEFAULT_WS_URL;
        }
        // If user passes ws://localhost:8080/ws, Spring STOMP raw websocket usually exposes /ws/websocket
        if (wsUrl.endsWith("/ws")) {
            wsUrl = wsUrl + "/websocket";
        }
        this.serverUri = URI.create(wsUrl);
        this.objectMapper = new ObjectMapper()
                .registerModule(new JavaTimeModule())
                .configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);
    }

    public void addWeatherUpdateListener(WeatherUpdateListener listener) {
        if (listener != null) {
            weatherListeners.add(listener);
        }
    }

    public void removeWeatherUpdateListener(WeatherUpdateListener listener) {
        weatherListeners.remove(listener);
    }

    public void addConnectionStatusListener(ConnectionStatusListener listener) {
        if (listener != null) {
            connectionListeners.add(listener);
        }
    }

    public void removeConnectionStatusListener(ConnectionStatusListener listener) {
        connectionListeners.remove(listener);
    }

    public synchronized void connect() {
        isRunning.set(true);
        initAndConnect();
    }

    public synchronized void disconnect() {
        isRunning.set(false);
        if (internalClient != null) {
            try {
                internalClient.close();
            } catch (Exception ignored) {
            }
        }
        setConnected(false);
    }

    public boolean isConnected() {
        return isConnected.get();
    }

    private synchronized void initAndConnect() {
        if (!isRunning.get()) {
            return;
        }

        try {
            if (internalClient != null) {
                try {
                    internalClient.close();
                } catch (Exception ignored) {}
            }

            internalClient = new org.java_websocket.client.WebSocketClient(serverUri) {
                @Override
                public void onOpen(ServerHandshake handshake) {
                    // Send STOMP CONNECT frame
                    sendStompConnect();
                }

                @Override
                public void onMessage(String message) {
                    handleIncomingMessage(message);
                }

                @Override
                public void onClose(int code, String reason, boolean remote) {
                    setConnected(false);
                    scheduleReconnect();
                }

                @Override
                public void onError(Exception ex) {
                    setConnected(false);
                    scheduleReconnect();
                }
            };

            internalClient.setConnectionLostTimeout(15);
            internalClient.connect();
        } catch (Exception e) {
            setConnected(false);
            scheduleReconnect();
        }
    }

    private void sendStompConnect() {
        String connectFrame = "CONNECT\n" +
                "accept-version:1.1,1.2\n" +
                "heart-beat:10000,10000\n" +
                "\n" +
                "\u0000";
        if (internalClient != null && internalClient.isOpen()) {
            internalClient.send(connectFrame);
        }
    }

    private void sendStompSubscribe(String destination, String subscriptionId) {
        String subscribeFrame = "SUBSCRIBE\n" +
                "id:" + subscriptionId + "\n" +
                "destination:" + destination + "\n" +
                "\n" +
                "\u0000";
        if (internalClient != null && internalClient.isOpen()) {
            internalClient.send(subscribeFrame);
        }
    }

    private void handleIncomingMessage(String rawMessage) {
        if (rawMessage == null || rawMessage.isBlank()) {
            return;
        }

        // STOMP CONNECTED response
        if (rawMessage.startsWith("CONNECTED")) {
            setConnected(true);
            sendStompSubscribe(TOPIC_WEATHER_UPDATES, "sub-weather-0");
            return;
        }

        // STOMP MESSAGE frame
        if (rawMessage.startsWith("MESSAGE")) {
            int bodyIndex = rawMessage.indexOf("\n\n");
            if (bodyIndex == -1) {
                bodyIndex = rawMessage.indexOf("\r\n\r\n");
                if (bodyIndex != -1) bodyIndex += 4;
            } else {
                bodyIndex += 2;
            }

            if (bodyIndex != -1 && bodyIndex < rawMessage.length()) {
                String body = rawMessage.substring(bodyIndex);
                if (body.endsWith("\u0000")) {
                    body = body.substring(0, body.length() - 1);
                }
                parseAndNotify(body.trim());
            }
            return;
        }

        // If raw JSON was sent directly without STOMP wrapping
        if (rawMessage.trim().startsWith("{")) {
            parseAndNotify(rawMessage.trim());
        }
    }

    private void parseAndNotify(String json) {
        if (json.isEmpty()) return;
        try {
            ApiClient.WeatherData weatherData = objectMapper.readValue(json, ApiClient.WeatherData.class);
            SwingUtilities.invokeLater(() -> {
                for (WeatherUpdateListener listener : weatherListeners) {
                    try {
                        listener.onWeatherUpdate(weatherData);
                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                }
            });
        } catch (Exception e) {
            // Silently ignore malformed non-weather messages (like heartbeats)
        }
    }

    private void setConnected(boolean connected) {
        boolean previous = isConnected.getAndSet(connected);
        if (previous != connected) {
            SwingUtilities.invokeLater(() -> {
                for (ConnectionStatusListener listener : connectionListeners) {
                    try {
                        listener.onConnectionStatusChanged(connected);
                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                }
            });
        }
    }

    private synchronized void scheduleReconnect() {
        if (!isRunning.get() || isReconnecting.get()) {
            return;
        }
        isReconnecting.set(true);
        reconnectExecutor.schedule(() -> {
            isReconnecting.set(false);
            if (isRunning.get() && (internalClient == null || !internalClient.isOpen())) {
                initAndConnect();
            }
        }, 5, TimeUnit.SECONDS);
    }
}
