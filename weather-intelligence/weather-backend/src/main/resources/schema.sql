-- Weather Intelligence System Database Schema (H2 Reference DDL)

CREATE TABLE IF NOT EXISTS users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,
    email VARCHAR(100),
    created_at TIMESTAMP NOT NULL,
    last_login TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cities (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    country VARCHAR(10) NOT NULL,
    latitude DOUBLE NOT NULL,
    longitude DOUBLE NOT NULL,
    state VARCHAR(100),
    created_at TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_cities_name ON cities(name);
CREATE INDEX IF NOT EXISTS idx_cities_name_country ON cities(name, country);

CREATE TABLE IF NOT EXISTS favorite_cities (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    city_id BIGINT NOT NULL,
    display_order INT NOT NULL DEFAULT 0,
    nickname VARCHAR(100),
    added_at TIMESTAMP NOT NULL,
    CONSTRAINT uk_favorite_user_city UNIQUE (user_id, city_id),
    CONSTRAINT fk_fav_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_fav_city FOREIGN KEY (city_id) REFERENCES cities(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_favorite_user_id ON favorite_cities(user_id);
CREATE INDEX IF NOT EXISTS idx_favorite_city_id ON favorite_cities(city_id);

CREATE TABLE IF NOT EXISTS weather_snapshots (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    city_id BIGINT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    temperature DOUBLE NOT NULL,
    feels_like DOUBLE NOT NULL,
    temp_min DOUBLE NOT NULL,
    temp_max DOUBLE NOT NULL,
    humidity INT NOT NULL,
    pressure INT NOT NULL,
    wind_speed DOUBLE NOT NULL,
    wind_direction INT NOT NULL,
    weather_main VARCHAR(50) NOT NULL,
    weather_desc VARCHAR(100) NOT NULL,
    icon_code VARCHAR(20) NOT NULL,
    cloudiness INT NOT NULL,
    visibility INT NOT NULL,
    source VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    CONSTRAINT fk_snapshot_city FOREIGN KEY (city_id) REFERENCES cities(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_weather_city_timestamp ON weather_snapshots(city_id, timestamp);

CREATE TABLE IF NOT EXISTS forecast_entries (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    city_id BIGINT NOT NULL,
    forecast_time TIMESTAMP NOT NULL,
    temperature DOUBLE NOT NULL,
    temp_min DOUBLE NOT NULL,
    temp_max DOUBLE NOT NULL,
    humidity INT NOT NULL,
    weather_main VARCHAR(50) NOT NULL,
    weather_desc VARCHAR(100) NOT NULL,
    icon_code VARCHAR(20) NOT NULL,
    pop DOUBLE NOT NULL,
    wind_speed DOUBLE NOT NULL,
    fetched_at TIMESTAMP NOT NULL,
    CONSTRAINT fk_forecast_city FOREIGN KEY (city_id) REFERENCES cities(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_forecast_city_forecast_time ON forecast_entries(city_id, forecast_time);

CREATE TABLE IF NOT EXISTS alert_rules (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    city_id BIGINT NOT NULL,
    alert_type VARCHAR(30) NOT NULL,
    threshold_value DOUBLE NOT NULL,
    condition_value VARCHAR(50),
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    last_triggered TIMESTAMP,
    created_at TIMESTAMP NOT NULL,
    CONSTRAINT fk_alert_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_alert_city FOREIGN KEY (city_id) REFERENCES cities(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_alert_user_enabled ON alert_rules(user_id, enabled);
CREATE INDEX IF NOT EXISTS idx_alert_city_id ON alert_rules(city_id);
CREATE INDEX IF NOT EXISTS idx_alert_type_enabled ON alert_rules(alert_type, enabled);

CREATE TABLE IF NOT EXISTS notifications (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    alert_rule_id BIGINT,
    title VARCHAR(150) NOT NULL,
    message VARCHAR(1000) NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    notification_type VARCHAR(20) NOT NULL DEFAULT 'INFO',
    created_at TIMESTAMP NOT NULL,
    CONSTRAINT fk_notification_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_notification_rule FOREIGN KEY (alert_rule_id) REFERENCES alert_rules(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_notifications_user_created ON notifications(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_notifications_user_read ON notifications(user_id, is_read);

CREATE TABLE IF NOT EXISTS audit_records (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT,
    action VARCHAR(50) NOT NULL,
    details VARCHAR(500),
    timestamp TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_audit_user_timestamp ON audit_records(user_id, timestamp);
