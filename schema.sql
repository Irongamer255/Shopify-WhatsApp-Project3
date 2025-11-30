-- Create Database
CREATE DATABASE IF NOT EXISTS shopify_whatsapp;
USE shopify_whatsapp;

-- Table: merchants
CREATE TABLE IF NOT EXISTS merchants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    api_key VARCHAR(255) UNIQUE NOT NULL,
    whatsapp_api_token VARCHAR(255),
    whatsapp_phone_number_id VARCHAR(255),
    tier INT DEFAULT 1
);

-- Table: orders
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    merchant_id INT,
    shopify_order_id VARCHAR(255) UNIQUE,
    order_number VARCHAR(255),
    customer_phone VARCHAR(255),
    customer_name VARCHAR(255),
    total_price VARCHAR(255),
    currency VARCHAR(50),
    financial_status VARCHAR(50),
    fulfillment_status VARCHAR(50),
    status ENUM('pending', 'confirmed', 'cancelled', 'shipped', 'delivered') DEFAULT 'pending',
    delivery_slot VARCHAR(255),
    delivery_instructions TEXT,
    tracking_number VARCHAR(255),
    tracking_url VARCHAR(255),
    courier_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (merchant_id) REFERENCES merchants(id)
);

-- Table: message_logs
CREATE TABLE IF NOT EXISTS message_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    message_type VARCHAR(50),
    status VARCHAR(50),
    whatsapp_message_id VARCHAR(255),
    content TEXT,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id)
);

-- Table: configs
CREATE TABLE IF NOT EXISTS configs (
    `key` VARCHAR(255) PRIMARY KEY,
    value VARCHAR(255),
    description VARCHAR(255)
);

-- Insert Sample Merchant (Default)
INSERT INTO merchants (name, api_key, tier) VALUES ('Default Merchant', 'default_api_key_123', 1);

-- Insert Sample Config
INSERT INTO configs (`key`, value, description) VALUES ('confirmation_delay_minutes', '30', 'Delay in minutes before sending confirmation');
