#!/bin/bash

# Parkinson's Diagnosis System - Startup Script
# Starts both backend (FastAPI) and frontend (Vite) servers

echo "🚀 Starting Parkinson's Diagnosis System..."
echo "=============================================="

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

# Kill any existing processes on ports 8000 and 5173
echo -e "${YELLOW}Checking for existing processes...${NC}"
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:5173 | xargs kill -9 2>/dev/null || true
sleep 1

# Start Backend
echo -e "\n${BLUE}📦 Starting Backend (FastAPI)...${NC}"
cd "$BACKEND_DIR"

if [ ! -d "ml_env" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv ml_env
fi

echo -e "${YELLOW}Activating virtual environment...${NC}"
source ml_env/bin/activate

echo -e "${YELLOW}Installing backend dependencies (if needed)...${NC}"
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt 2>/dev/null || pip install --quiet fastapi uvicorn 'python-jose[cryptography]' 'passlib[bcrypt]' python-multipart sqlalchemy psycopg2-binary Pillow numpy tensorflow scikit-learn librosa soundfile email-validator python-dotenv pydantic-settings

echo -e "${GREEN}✅ Backend dependencies ready${NC}"
echo -e "${BLUE}Starting uvicorn server on http://localhost:8000${NC}"

# Start backend in background
nohup ./ml_env/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}"

# Wait for backend to start
echo -e "${YELLOW}Waiting for backend to initialize...${NC}"
sleep 3

# Start Frontend
echo -e "\n${BLUE}🎨 Starting Frontend (Vite + React)...${NC}"
cd "$FRONTEND_DIR"

if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    npm install
fi

echo -e "${GREEN}✅ Frontend dependencies ready${NC}"
echo -e "${BLUE}Starting development server on http://localhost:5173${NC}"

# Start frontend in background
nohup npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!
echo -e "${GREEN}✅ Frontend started (PID: $FRONTEND_PID)${NC}"

# Wait for frontend to start
sleep 3

# Display status
echo -e "\n${GREEN}=============================================="
echo -e "🎉 System Started Successfully!"
echo -e "==============================================${NC}"
echo -e ""
echo -e "${BLUE}🔗 Access Points:${NC}"
echo -e "   Frontend:  ${GREEN}http://localhost:5173${NC}"
echo -e "   Backend:   ${GREEN}http://localhost:8000${NC}"
echo -e "   API Docs:  ${GREEN}http://localhost:8000/docs${NC}"
echo -e ""
echo -e "${BLUE}📊 Process IDs:${NC}"
echo -e "   Backend:  ${YELLOW}$BACKEND_PID${NC}"
echo -e "   Frontend: ${YELLOW}$FRONTEND_PID${NC}"
echo -e ""
echo -e "${BLUE}📝 Log Files:${NC}"
echo -e "   Backend:  ${YELLOW}$BACKEND_DIR/backend.log${NC}"
echo -e "   Frontend: ${YELLOW}$FRONTEND_DIR/frontend.log${NC}"
echo -e ""
echo -e "${YELLOW}💡 To stop servers:${NC}"
echo -e "   kill $BACKEND_PID $FRONTEND_PID"
echo -e "   or use: ${YELLOW}./stop_servers.sh${NC}"
echo -e ""
echo -e "${GREEN}=============================================="
echo -e "Press Ctrl+C to view logs, or close terminal${NC}"
echo -e "${GREEN}==============================================${NC}"

# Save PIDs to file for stopping later
echo "$BACKEND_PID" > "$SCRIPT_DIR/.backend.pid"
echo "$FRONTEND_PID" > "$SCRIPT_DIR/.frontend.pid"

# Follow logs
echo -e "\n${BLUE}📋 Following logs (Ctrl+C to stop)...${NC}\n"
tail -f "$BACKEND_DIR/backend.log" "$FRONTEND_DIR/frontend.log"
