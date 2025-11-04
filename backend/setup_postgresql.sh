#!/bin/bash

# PostgreSQL Database Setup Script for ParkinsonCare
# This script sets up PostgreSQL database and user for the application

echo "🐘 Setting up PostgreSQL for ParkinsonCare..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Database configuration
DB_NAME="parkinson_db"
TEST_DB_NAME="parkinson_test_db"
DB_USER="parkinson_user"
DB_PASSWORD="parkinson123"

echo -e "${BLUE}Database Configuration:${NC}"
echo -e "  Main Database: ${YELLOW}$DB_NAME${NC}"
echo -e "  Test Database: ${YELLOW}$TEST_DB_NAME${NC}"
echo -e "  User: ${YELLOW}$DB_USER${NC}"
echo ""

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo -e "${RED}❌ PostgreSQL is not installed!${NC}"
    echo -e "${YELLOW}Please install PostgreSQL first:${NC}"
    echo -e "${BLUE}  Ubuntu/Debian: sudo apt-get install postgresql postgresql-contrib${NC}"
    echo -e "${BLUE}  CentOS/RHEL: sudo yum install postgresql-server postgresql-contrib${NC}"
    echo -e "${BLUE}  macOS: brew install postgresql${NC}"
    echo -e "${BLUE}  Arch Linux: sudo pacman -S postgresql${NC}"
    exit 1
fi

# Check if PostgreSQL service is running
if ! sudo systemctl is-active --quiet postgresql; then
    echo -e "${YELLOW}⚠️  PostgreSQL service is not running. Starting it...${NC}"
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
    echo -e "${GREEN}✅ PostgreSQL service started${NC}"
fi

# Function to run PostgreSQL commands
run_psql() {
    sudo -u postgres psql -c "$1"
}

echo -e "${BLUE}🔧 Setting up database and user...${NC}"

# Create database user
echo -e "${YELLOW}Creating user '$DB_USER'...${NC}"
if run_psql "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1; then
    echo -e "${YELLOW}User '$DB_USER' already exists, updating password...${NC}"
    run_psql "ALTER USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
else
    run_psql "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
    echo -e "${GREEN}✅ User '$DB_USER' created${NC}"
fi

# Grant privileges to user
run_psql "ALTER USER $DB_USER CREATEDB;"
run_psql "ALTER USER $DB_USER WITH SUPERUSER;"

# Create main database
echo -e "${YELLOW}Creating database '$DB_NAME'...${NC}"
if run_psql "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" | grep -q 1; then
    echo -e "${YELLOW}Database '$DB_NAME' already exists${NC}"
else
    run_psql "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
    echo -e "${GREEN}✅ Database '$DB_NAME' created${NC}"
fi

# Create test database
echo -e "${YELLOW}Creating test database '$TEST_DB_NAME'...${NC}"
if run_psql "SELECT 1 FROM pg_database WHERE datname='$TEST_DB_NAME'" | grep -q 1; then
    echo -e "${YELLOW}Test database '$TEST_DB_NAME' already exists${NC}"
else
    run_psql "CREATE DATABASE $TEST_DB_NAME OWNER $DB_USER;"
    echo -e "${GREEN}✅ Test database '$TEST_DB_NAME' created${NC}"
fi

# Grant all privileges
run_psql "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
run_psql "GRANT ALL PRIVILEGES ON DATABASE $TEST_DB_NAME TO $DB_USER;"

echo ""
echo -e "${GREEN}🎉 PostgreSQL setup completed successfully!${NC}"
echo ""
echo -e "${BLUE}Connection Details:${NC}"
echo -e "  Host: ${YELLOW}localhost${NC}"
echo -e "  Port: ${YELLOW}5432${NC}"
echo -e "  Main Database: ${YELLOW}$DB_NAME${NC}"
echo -e "  Test Database: ${YELLOW}$TEST_DB_NAME${NC}"
echo -e "  Username: ${YELLOW}$DB_USER${NC}"
echo -e "  Password: ${YELLOW}$DB_PASSWORD${NC}"
echo ""
echo -e "${BLUE}Connection URLs:${NC}"
echo -e "  Main: ${YELLOW}postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME${NC}"
echo -e "  Test: ${YELLOW}postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$TEST_DB_NAME${NC}"
echo ""
echo -e "${GREEN}✅ You can now run the application with PostgreSQL!${NC}"

# Test connection
echo -e "${BLUE}🔍 Testing database connection...${NC}"
if PGPASSWORD=$DB_PASSWORD psql -h localhost -U $DB_USER -d $DB_NAME -c "SELECT version();" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Database connection test successful!${NC}"
else
    echo -e "${RED}❌ Database connection test failed!${NC}"
    echo -e "${YELLOW}Please check PostgreSQL service and credentials${NC}"
fi