# Database Schema Documentation

## Overview

The ParkinsonCare platform uses **PostgreSQL** as its primary and only database management system. This document outlines the database schema, tables, and relationships.

## Database Configuration

- **Database System**: PostgreSQL 17.5+
- **Connection**: `postgresql://parkinson_user:parkinson123@localhost:5432/parkinson_db`
- **Test Database**: `postgresql://parkinson_user:parkinson123@localhost:5432/parkinson_test_db`
- **ORM**: SQLAlchemy 2.0+

## Database Setup

### Prerequisites

1. PostgreSQL installed and running
2. Python environment with required packages

### Setup Commands

```bash
# 1. Install PostgreSQL (Arch Linux)
sudo pacman -S postgresql

# 2. Initialize PostgreSQL
sudo -u postgres initdb -D /var/lib/postgres/data

# 3. Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 4. Run the setup script
cd backend
./setup_postgresql.sh

# 5. Create database tables
python db_setup.py
```

## Database Tables

### Core Tables

#### 1. users
Primary user authentication and profile table.

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    role VARCHAR(20) CHECK (role IN ('patient', 'doctor', 'admin')) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. patients
Extended patient information linked to users.

```sql
CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    date_of_birth DATE,
    gender VARCHAR(10),
    phone VARCHAR(20),
    address TEXT,
    emergency_contact VARCHAR(100),
    emergency_phone VARCHAR(20),
    medical_history TEXT,
    assigned_doctor_id INTEGER REFERENCES doctors(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 3. doctors
Doctor-specific information and credentials.

```sql
CREATE TABLE doctors (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    license_number VARCHAR(50) UNIQUE,
    specialization VARCHAR(100),
    years_of_experience INTEGER,
    hospital_affiliation VARCHAR(200),
    credentials TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Medical Data Tables

#### 4. medical_data
Stores uploaded medical files and metadata.

```sql
CREATE TABLE medical_data (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    data_type VARCHAR(50) CHECK (data_type IN ('mri', 'ecg', 'voice', 'handwriting', 'blood_test', 'other')),
    file_path VARCHAR(500),
    file_name VARCHAR(255),
    file_size INTEGER,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB,
    processed BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 5. analysis_results
AI/ML analysis results for medical data.

```sql
CREATE TABLE analysis_results (
    id SERIAL PRIMARY KEY,
    medical_data_id INTEGER REFERENCES medical_data(id) ON DELETE CASCADE,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    analysis_type VARCHAR(50),
    model_version VARCHAR(20),
    confidence_score DECIMAL(5,4),
    result_data JSONB,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 6. diagnosis_reports
Clinical diagnosis reports from doctors.

```sql
CREATE TABLE diagnosis_reports (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    doctor_id INTEGER REFERENCES doctors(id) ON DELETE CASCADE,
    report_date DATE DEFAULT CURRENT_DATE,
    diagnosis VARCHAR(200),
    severity_level INTEGER CHECK (severity_level BETWEEN 0 AND 4),
    symptoms TEXT,
    clinical_notes TEXT,
    recommended_treatment TEXT,
    follow_up_date DATE,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Supporting Tables

#### 7. lifestyle_suggestions
RAG-powered lifestyle recommendations.

```sql
CREATE TABLE lifestyle_suggestions (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    suggestion_type VARCHAR(50),
    title VARCHAR(200),
    description TEXT,
    priority_level INTEGER CHECK (priority_level BETWEEN 1 AND 5),
    is_active BOOLEAN DEFAULT true,
    generated_by VARCHAR(50) DEFAULT 'AI',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 8. audit_logs
System audit trail for security and compliance.

```sql
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(100),
    resource_type VARCHAR(50),
    resource_id INTEGER,
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Database Indexes

For optimal performance, the following indexes are recommended:

```sql
-- User lookups
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);

-- Patient-Doctor relationships
CREATE INDEX idx_patients_user_id ON patients(user_id);
CREATE INDEX idx_patients_doctor_id ON patients(assigned_doctor_id);
CREATE INDEX idx_doctors_user_id ON doctors(user_id);

-- Medical data queries
CREATE INDEX idx_medical_data_patient_id ON medical_data(patient_id);
CREATE INDEX idx_medical_data_type ON medical_data(data_type);
CREATE INDEX idx_medical_data_date ON medical_data(upload_date);

-- Analysis results
CREATE INDEX idx_analysis_results_patient_id ON analysis_results(patient_id);
CREATE INDEX idx_analysis_results_medical_data_id ON analysis_results(medical_data_id);

-- Diagnosis reports
CREATE INDEX idx_diagnosis_reports_patient_id ON diagnosis_reports(patient_id);
CREATE INDEX idx_diagnosis_reports_doctor_id ON diagnosis_reports(doctor_id);
CREATE INDEX idx_diagnosis_reports_date ON diagnosis_reports(report_date);

-- Audit logs
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
```

## Relationships

```mermaid
erDiagram
    users ||--o{ patients : "user_id"
    users ||--o{ doctors : "user_id"
    doctors ||--o{ patients : "assigned_doctor_id"
    patients ||--o{ medical_data : "patient_id"
    patients ||--o{ diagnosis_reports : "patient_id"
    patients ||--o{ lifestyle_suggestions : "patient_id"
    patients ||--o{ analysis_results : "patient_id"
    doctors ||--o{ diagnosis_reports : "doctor_id"
    medical_data ||--o{ analysis_results : "medical_data_id"
    users ||--o{ audit_logs : "user_id"
```

## Configuration

### Connection Pool Settings

```python
# PostgreSQL optimized settings
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=10,
    max_overflow=20
)
```

### Environment Variables

```bash
# Primary database
DATABASE_URL=postgresql://parkinson_user:parkinson123@localhost:5432/parkinson_db

# Test database
DATABASE_TEST_URL=postgresql://parkinson_user:parkinson123@localhost:5432/parkinson_test_db
```

## Migration Commands

```bash
# Generate migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Backup and Restore

### Backup

```bash
# Full database backup
pg_dump -h localhost -U parkinson_user -d parkinson_db > backup.sql

# Schema only
pg_dump -h localhost -U parkinson_user -d parkinson_db --schema-only > schema.sql

# Data only
pg_dump -h localhost -U parkinson_user -d parkinson_db --data-only > data.sql
```

### Restore

```bash
# Restore full database
psql -h localhost -U parkinson_user -d parkinson_db < backup.sql

# Restore with create database
psql -h localhost -U postgres -c "CREATE DATABASE parkinson_db_restore OWNER parkinson_user;"
psql -h localhost -U parkinson_user -d parkinson_db_restore < backup.sql
```

## Performance Tuning

### PostgreSQL Configuration

Add to `postgresql.conf`:

```conf
# Memory settings
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB

# Connection settings
max_connections = 200

# Logging
log_statement = 'mod'
log_min_duration_statement = 1000

# Checkpoint settings
checkpoint_completion_target = 0.9
```

## Security

### User Privileges

```sql
-- Create read-only user for reporting
CREATE USER parkinson_reader WITH PASSWORD 'read_password';
GRANT CONNECT ON DATABASE parkinson_db TO parkinson_reader;
GRANT USAGE ON SCHEMA public TO parkinson_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO parkinson_reader;

-- Create backup user
CREATE USER parkinson_backup WITH PASSWORD 'backup_password';
GRANT CONNECT ON DATABASE parkinson_db TO parkinson_backup;
GRANT USAGE ON SCHEMA public TO parkinson_backup;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO parkinson_backup;
```

### SSL Configuration

For production, ensure SSL is enabled:

```bash
# Update connection string for SSL
DATABASE_URL=postgresql://parkinson_user:password@localhost:5432/parkinson_db?sslmode=require
```

## Monitoring

### Common Queries

```sql
-- Check database size
SELECT pg_size_pretty(pg_database_size('parkinson_db'));

-- Table sizes
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size(tablename::regclass)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(tablename::regclass) DESC;

-- Active connections
SELECT count(*) FROM pg_stat_activity WHERE datname = 'parkinson_db';

-- Long running queries
SELECT pid, now() - pg_stat_activity.query_start AS duration, query 
FROM pg_stat_activity 
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';
```