-- Weather Intelligence System Default Seed Data

-- Users (BCrypt encoded passwords)
-- admin / admin123 ($2a$10$8.UnVuG9HHgffUDAlk8qfOuVGkqRzgVymGe07xd00DMxs.AQubh4a)
-- user / user123 ($2a$10$wT1.H2a8K1j9K2vMwq/m8OCqZtJ4K3a/nSjP0l5F9d6J6XnOQk4cW)

MERGE INTO users (id, username, password_hash, role, email, created_at)
KEY(username)
VALUES (1, 'admin', '$2a$10$8.UnVuG9HHgffUDAlk8qfOuVGkqRzgVymGe07xd00DMxs.AQubh4a', 'ADMIN', 'admin@weatherintel.com', CURRENT_TIMESTAMP);

MERGE INTO users (id, username, password_hash, role, email, created_at)
KEY(username)
VALUES (2, 'user', '$2a$10$wT1.H2a8K1j9K2vMwq/m8OCqZtJ4K3a/nSjP0l5F9d6J6XnOQk4cW', 'USER', 'user@weatherintel.com', CURRENT_TIMESTAMP);

-- Default Cities
MERGE INTO cities (id, name, country, latitude, longitude, state, created_at)
KEY(name, country)
VALUES (1, 'London', 'GB', 51.5074, -0.1278, 'Greater London', CURRENT_TIMESTAMP);

MERGE INTO cities (id, name, country, latitude, longitude, state, created_at)
KEY(name, country)
VALUES (2, 'New York', 'US', 40.7128, -74.0060, 'New York', CURRENT_TIMESTAMP);

MERGE INTO cities (id, name, country, latitude, longitude, state, created_at)
KEY(name, country)
VALUES (3, 'Tokyo', 'JP', 35.6762, 139.6503, 'Tokyo', CURRENT_TIMESTAMP);

MERGE INTO cities (id, name, country, latitude, longitude, state, created_at)
KEY(name, country)
VALUES (4, 'Mumbai', 'IN', 19.0760, 72.8777, 'Maharashtra', CURRENT_TIMESTAMP);

MERGE INTO cities (id, name, country, latitude, longitude, state, created_at)
KEY(name, country)
VALUES (5, 'Sydney', 'AU', -33.8688, 151.2093, 'New South Wales', CURRENT_TIMESTAMP);

MERGE INTO cities (id, name, country, latitude, longitude, state, created_at)
KEY(name, country)
VALUES (6, 'Paris', 'FR', 48.8566, 2.3522, 'Île-de-France', CURRENT_TIMESTAMP);
