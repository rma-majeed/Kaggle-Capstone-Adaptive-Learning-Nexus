#!/bin/bash

# Educational Learning Coach - Start All Services
# This script starts all required services for the application

set -e

echo "🚀 Starting Educational Learning Coach..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Navigate to project root (script's directory)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$SCRIPT_DIR"
cd "$PROJECT_DIR"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo -e "${RED}Error: Python virtual environment not found.${NC}"
    echo "Please create it first: python3 -m venv venv"
    exit 1
fi

# Activate Python venv
source venv/bin/activate

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to kill process on port
kill_port() {
    if check_port $1; then
        echo -e "${YELLOW}Port $1 is in use. Killing existing process...${NC}"
        lsof -ti :$1 | xargs -r kill -9 2>/dev/null || true
        sleep 1
    fi
}

# Clean up any existing processes
echo "🧹 Cleaning up existing processes..."
kill_port 8000   # ADK Web
kill_port 10010  # A2A RAG Agent
kill_port 3000   # Frontend

echo ""

# Start A2A RAG Agent (background)
echo -e "${GREEN}📚 Starting A2A RAG Agent on port 10010...${NC}"
cd "$PROJECT_DIR/agents/Teacher_Flow"
python -m a2a_rag_agent > /tmp/a2a_rag.log 2>&1 &
A2A_PID=$!
cd "$PROJECT_DIR"

# Wait for A2A to start
echo "   Waiting for A2A server to initialize..."
sleep 5

if check_port 10010; then
    echo -e "   ${GREEN}✅ A2A RAG Agent started (PID: $A2A_PID)${NC}"
else
    echo -e "   ${YELLOW}⚠️  A2A RAG Agent may not have started correctly${NC}"
    echo -e "   ${YELLOW}   Check logs: tail -f /tmp/a2a_rag.log${NC}"
fi

# Start ADK Web Server (background)
echo ""
echo -e "${GREEN}🤖 Starting ADK Web Server on port 8000...${NC}"
adk web --session_service_uri="sqlite:///agents/student_flow/data/student_sessions.db" --allow_origins="http://localhost:3000" agents/ > /tmp/adk_web.log 2>&1 &
ADK_PID=$!

# Wait for ADK to start
echo "   Waiting for ADK server to initialize..."
sleep 5

if check_port 8000; then
    echo -e "   ${GREEN}✅ ADK Web Server started (PID: $ADK_PID)${NC}"
else
    echo -e "   ${YELLOW}⚠️  ADK Web Server may not have started correctly${NC}"
    echo -e "   ${YELLOW}   Check logs: tail -f /tmp/adk_web.log${NC}"
fi

# Start Frontend with Python HTTP Server (background)
echo ""
echo -e "${GREEN}🎨 Starting Frontend on port 3000...${NC}"
cd "$PROJECT_DIR/frontend"
python -m http.server 3000 > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
cd "$PROJECT_DIR"

# Wait for frontend to start
sleep 2

if check_port 3000; then
    echo -e "   ${GREEN}✅ Frontend started (PID: $FRONTEND_PID)${NC}"
else
    echo -e "   ${YELLOW}⚠️  Frontend may not have started correctly${NC}"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo -e "${GREEN}✅ All services started!${NC}"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo -e "${BLUE}📍 Access Points:${NC}"
echo "   Frontend:   http://localhost:3000"
echo "   ADK API:    http://localhost:8000"
echo "   A2A Agent:  http://localhost:10010"
echo ""
echo -e "${BLUE}📋 Logs:${NC}"
echo "   A2A RAG:    tail -f /tmp/a2a_rag.log"
echo "   ADK Web:    tail -f /tmp/adk_web.log"
echo "   Frontend:   tail -f /tmp/frontend.log"
echo ""
echo -e "${YELLOW}To stop all services:${NC}"
echo "   pkill -f 'adk web'; pkill -f 'a2a_rag_agent'; pkill -f 'http.server 3000'"
echo ""
echo -e "${BLUE}Press Ctrl+C to stop all services${NC}"

# Trap Ctrl+C and cleanup
cleanup() {
    echo ""
    echo "🛑 Stopping all services..."
    kill $A2A_PID $ADK_PID $FRONTEND_PID 2>/dev/null || true
    pkill -f "adk web" 2>/dev/null || true
    pkill -f "a2a_rag_agent" 2>/dev/null || true
    pkill -f "http.server 3000" 2>/dev/null || true
    echo "👋 Goodbye!"
    exit 0
}

trap cleanup INT TERM

# Keep script running
wait
