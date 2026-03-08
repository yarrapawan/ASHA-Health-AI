-- ============================================================
-- ASHA Sahayak — MySQL Schema
-- Run: mysql -u root -p < schema.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS asha_sahayak CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE asha_sahayak;

-- Patients table
CREATE TABLE IF NOT EXISTS patients (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    patient_id  VARCHAR(20)  UNIQUE NOT NULL,   -- e.g. ASHA001
    name        VARCHAR(100) NOT NULL,
    age         INT          NOT NULL,
    gender      ENUM('Male','Female','Other') NOT NULL,
    village     VARCHAR(100),
    phone       VARCHAR(15),
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_patient_id (patient_id)
);

-- Visits / Sessions table
CREATE TABLE IF NOT EXISTS visits (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    patient_id    VARCHAR(20) NOT NULL,
    visit_time    DATETIME DEFAULT CURRENT_TIMESTAMP,
    lang          VARCHAR(5)  DEFAULT 'en',
    model         VARCHAR(50),
    triage_level  ENUM('EMERGENCY','URGENT','MONITOR','HOME') NULL,
    chat_log      LONGTEXT,                       -- JSON array of messages
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    INDEX idx_patient_visit (patient_id, visit_time)
);

-- Sample data (optional — remove in production)
INSERT IGNORE INTO patients (patient_id, name, age, gender, village, phone)
VALUES
  ('DEMO001', 'Sunita Devi',  32, 'Female', 'Rampur',    '9876543210'),
  ('DEMO002', 'Ramu Kumar',   45, 'Male',   'Chandpur',  '9876543211'),
  ('DEMO003', 'Meena Bai',    28, 'Female', 'Govindpur', '9876543212');