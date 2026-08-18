CREATE DATABASE IF NOT EXISTS emotilearn_db;

USE emotilearn_db;

DROP TABLE IF EXISTS users;

CREATE TABLE users(
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    google_id VARCHAR(255),
    profile_image TEXT,
    role ENUM('student','teacher','parent','admin') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
