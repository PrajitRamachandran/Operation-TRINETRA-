-- Database initialization script for Convoy Routing System
-- This script creates the necessary database structure

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS convoy_routing CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Use the database
USE convoy_routing;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'operator', 'viewer') DEFAULT 'viewer',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create convoys table
CREATE TABLE IF NOT EXISTS convoys (
    id INT AUTO_INCREMENT PRIMARY KEY,
    call_sign VARCHAR(50) UNIQUE NOT NULL,
    status ENUM('planning', 'active', 'completed', 'cancelled', 'emergency') DEFAULT 'planning',
    current_location POINT NOT NULL,
    destination POINT NOT NULL,
    speed_kmph DECIMAL(5,2) DEFAULT 0.00,
    eta TIMESTAMP NULL,
    fuel_level DECIMAL(5,2) DEFAULT 100.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    SPATIAL INDEX idx_current_location (current_location),
    SPATIAL INDEX idx_destination (destination)
);

-- Create threats table
CREATE TABLE IF NOT EXISTS threats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    classification ENUM('low', 'medium', 'high', 'critical') NOT NULL,
    source_type ENUM('intelligence', 'sensor', 'manual', 'satellite') NOT NULL,
    verified_status ENUM('unverified', 'confirmed', 'false_positive') DEFAULT 'unverified',
    location POINT NOT NULL,
    description TEXT,
    confidence_score DECIMAL(3,2) DEFAULT 0.00,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    verified_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    SPATIAL INDEX idx_location (location)
);

-- Create routes table
CREATE TABLE IF NOT EXISTS routes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    convoy_id INT NOT NULL,
    route_mode ENUM('balance', 'stealth', 'speed') NOT NULL,
    path_geometry GEOMETRY NOT NULL,
    total_distance_km DECIMAL(10,2) NOT NULL,
    estimated_fuel_liters DECIMAL(10,2) NOT NULL,
    estimated_duration_minutes INT NOT NULL,
    risk_score DECIMAL(3,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (convoy_id) REFERENCES convoys(id) ON DELETE CASCADE,
    SPATIAL INDEX idx_path_geometry (path_geometry)
);

-- Create alerts table
CREATE TABLE IF NOT EXISTS alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    severity ENUM('info', 'warning', 'critical', 'emergency') NOT NULL,
    message TEXT NOT NULL,
    alert_type ENUM('system', 'security', 'operational', 'maintenance') NOT NULL,
    convoy_id INT NULL,
    threat_id INT NULL,
    is_acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_by INT NULL,
    acknowledged_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (convoy_id) REFERENCES convoys(id) ON DELETE SET NULL,
    FOREIGN KEY (threat_id) REFERENCES threats(id) ON DELETE SET NULL,
    FOREIGN KEY (acknowledged_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Create missions table
CREATE TABLE IF NOT EXISTS missions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    call_sign VARCHAR(50) NOT NULL,
    start_location POINT NOT NULL,
    end_location POINT NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NULL,
    final_status ENUM('completed', 'failed', 'cancelled') DEFAULT NULL,
    total_distance_km DECIMAL(10,2) DEFAULT 0.00,
    fuel_consumed_liters DECIMAL(10,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    SPATIAL INDEX idx_start_location (start_location),
    SPATIAL INDEX idx_end_location (end_location)
);

-- Create system_status table
CREATE TABLE IF NOT EXISTS system_status (
    id INT AUTO_INCREMENT PRIMARY KEY,
    status ENUM('operational', 'degraded', 'offline') DEFAULT 'operational',
    weather JSON,
    last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Insert default admin user (password: admin123 - CHANGE IN PRODUCTION!)
INSERT IGNORE INTO users (username, email, hashed_password, role) VALUES 
('admin', 'admin@convoy.local', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8Kz8Kz8K', 'admin');

-- Insert sample system status
INSERT IGNORE INTO system_status (status, weather) VALUES 
('operational', '{"temperature_celsius": 25, "humidity_percent": 60, "visibility_km": 10}');

-- Create indexes for better performance
CREATE INDEX idx_convoys_status ON convoys(status);
CREATE INDEX idx_convoys_created_at ON convoys(created_at);
CREATE INDEX idx_threats_classification ON threats(classification);
CREATE INDEX idx_threats_verified_status ON threats(verified_status);
CREATE INDEX idx_alerts_severity ON alerts(severity);
CREATE INDEX idx_alerts_created_at ON alerts(created_at);
CREATE INDEX idx_missions_final_status ON missions(final_status);

-- Create views for common queries
CREATE OR REPLACE VIEW active_convoys AS
SELECT 
    c.*,
    ST_X(c.current_location) as current_lat,
    ST_Y(c.current_location) as current_lon,
    ST_X(c.destination) as dest_lat,
    ST_Y(c.destination) as dest_lon
FROM convoys c 
WHERE c.status IN ('active', 'planning');

CREATE OR REPLACE VIEW confirmed_threats AS
SELECT 
    t.*,
    ST_X(t.location) as lat,
    ST_Y(t.location) as lon
FROM threats t 
WHERE t.verified_status = 'confirmed';

-- Grant permissions to convoy_user
GRANT SELECT, INSERT, UPDATE, DELETE ON convoy_routing.* TO 'convoy_user'@'%';
FLUSH PRIVILEGES;
