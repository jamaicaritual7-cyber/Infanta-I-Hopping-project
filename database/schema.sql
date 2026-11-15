CREATE DATABASE IF NOT EXISTS infanta_i_hopping CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE infanta_i_hopping;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    contact_number VARCHAR(30) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'customer',
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS otp_codes (
    id INT AUTO_INCREMENT PRIMARY KEY, user_id INT NOT NULL, code_hash VARCHAR(255) NOT NULL,
    expires_at DATETIME NOT NULL, attempts INT NOT NULL DEFAULT 0, used_at DATETIME,
    sent_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_otp_user (user_id)
);

CREATE TABLE IF NOT EXISTS boats (
    id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100) NOT NULL UNIQUE,
    fuel_type VARCHAR(50) NOT NULL DEFAULT 'Diesel', passenger_capacity INT NOT NULL,
    description TEXT, photograph_path VARCHAR(255), is_active BOOLEAN NOT NULL DEFAULT TRUE,
    availability_status VARCHAR(30) NOT NULL DEFAULT 'available',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS destinations (
    id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(150) NOT NULL,
    municipality VARCHAR(100) NOT NULL, province VARCHAR(100) NOT NULL DEFAULT 'Quezon',
    latitude DECIMAL(10,7), longitude DECIMAL(10,7), google_maps_url VARCHAR(500),
    straight_line_distance_km DECIMAL(8,2), straight_line_distance_nm DECIMAL(8,2),
    verified_sailing_distance_km DECIMAL(8,2), estimated_travel_minutes INT,
    coordinate_source VARCHAR(255), verification_status VARCHAR(30) NOT NULL DEFAULT 'unverified',
    verification_date DATE, description TEXT, image_path VARCHAR(255), is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS packages (
    id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(180) NOT NULL,
    municipality VARCHAR(100) NOT NULL, package_type VARCHAR(30) NOT NULL DEFAULT 'nearby',
    description TEXT, route_status VARCHAR(30) NOT NULL DEFAULT 'proposed', is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS package_destinations (
    package_id INT NOT NULL, destination_id INT NOT NULL, stop_order INT NOT NULL DEFAULT 1,
    PRIMARY KEY (package_id, destination_id),
    FOREIGN KEY (package_id) REFERENCES packages(id), FOREIGN KEY (destination_id) REFERENCES destinations(id)
);

CREATE TABLE IF NOT EXISTS pricing (
    id INT AUTO_INCREMENT PRIMARY KEY, package_id INT NOT NULL, amount DECIMAL(12,2) NOT NULL,
    currency CHAR(3) NOT NULL DEFAULT 'PHP', price_type VARCHAR(30) NOT NULL DEFAULT 'provisional',
    valid_from DATE, valid_until DATE, is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (package_id) REFERENCES packages(id)
);
