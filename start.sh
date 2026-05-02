#!/bin/bash
# SENTI-MIND startup script (Linux compatible)

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo "========================================"
echo "  SENTI-MIND Mental Health Analyzer"
echo "========================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

BACKEND_URL="http://127.0.0.1:8000"
FRONTEND_URL="http://127.0.0.1:5173"

# Function to check if a port is in use
check_port() {
    lsof -i:$1 > /dev/null 2>&1
}

# Function to cleanup processes on exit
cleanup() {
    echo ""
    echo "Shutting down services..."
    if [ -n "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo "Backend stopped"
    fi
    if [ -n "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo "Frontend stopped"
    fi
    exit 0
}

trap cleanup INT TERM

# Check and install backend dependencies
echo -e "${YELLOW}Checking backend environment...${NC}"
if [ ! -d "backend/.venv" ]; then
    echo -e "${YELLOW}Creating backend virtual environment...${NC}"
    cd backend
    python3 -m venv .venv
    source .venv/bin/activate
    echo -e "${YELLOW}Installing python dependencies...${NC}"
    pip install -r requirements.txt
    echo -e "${YELLOW}Downloading spaCy model...${NC}"
    python -m spacy download en_core_web_sm
    cd ..
    echo -e "${GREEN}Backend setup complete!${NC}"
fi

# Ensure .env exists
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    echo -e "${YELLOW}Creating .env from .env.example...${NC}"
    cp .env.example .env
    echo -e "${RED}IMPORTANT: Please update .env with your API keys (HF_API_TOKEN, etc.)${NC}"
fi

# Check and install frontend dependencies
echo -e "${YELLOW}Checking frontend environment...${NC}"
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    cd frontend
    npm install
    cd ..
    echo -e "${GREEN}Frontend setup complete!${NC}"
fi

echo "Checking services..."
echo ""

# Start Backend
if check_port 8000; then
    echo -e "${YELLOW}Backend already running on port 8000${NC}"
else
    echo -e "${GREEN}Starting backend...${NC}"
    cd backend
    .venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 &
    BACKEND_PID=$!
    cd ..
    echo -e "${GREEN}Backend PID: $BACKEND_PID${NC}"

    # Wait for backend to be ready
    echo -n "Waiting for backend..."
    for i in {1..30}; do
        if curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
            echo -e " ${GREEN}Ready!${NC}"
            break
        fi
        echo -n "."
        sleep 0.5
    done
    echo ""
fi

echo ""

# Start Frontend
if check_port 5173; then
    echo -e "${YELLOW}Frontend already running on port 5173${NC}"
else
    echo -e "${GREEN}Starting frontend...${NC}"
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    echo -e "${GREEN}Frontend PID: $FRONTEND_PID${NC}"

    # Wait for frontend
    echo -n "Waiting for frontend..."
    for i in {1..30}; do
        if curl -s http://127.0.0.1:5173 > /dev/null 2>&1; then
            echo -e " ${GREEN}Ready!${NC}"
            break
        fi
        echo -n "."
        sleep 0.5
    done
    echo ""
fi

echo ""
echo "========================================"
echo -e "${GREEN}All services running!${NC}"
echo "========================================"
echo ""
echo "Backend API:  $BACKEND_URL"
echo "API Docs:     $BACKEND_URL/docs"
echo "Frontend:     $FRONTEND_URL"
echo ""
echo -e "Open ${YELLOW}$FRONTEND_URL${NC} in your browser"
echo ""
echo "Press Ctrl+C to stop all services"
echo "========================================"

# Keep script running
tail -f /dev/null &
TAIL_PID=$!
wait $TAIL_PID
