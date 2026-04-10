#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  MCUBE LUNA AI - Backend Server        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}\n"

# Get local IP address
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    LOCAL_IP=$(ipconfig getifaddr en0)
    if [ -z "$LOCAL_IP" ]; then
        LOCAL_IP=$(ipconfig getifaddr en1)
    fi
else
    # Linux
    LOCAL_IP=$(hostname -I | awk '{print $1}')
fi

PORT=8000

echo -e "${GREEN}✓ Backend Server Configuration${NC}"
echo -e "  Local IP: ${YELLOW}$LOCAL_IP${NC}"
echo -e "  Port: ${YELLOW}$PORT${NC}\n"

echo -e "${GREEN}✓ Access URLs:${NC}"
echo -e "  Local:    ${YELLOW}http://127.0.0.1:$PORT${NC}"
echo -e "  Network:  ${YELLOW}http://$LOCAL_IP:$PORT${NC}"
echo -e "  Admin:    ${YELLOW}http://$LOCAL_IP:$PORT/admin.html${NC}"
echo -e "  Docs:     ${YELLOW}http://$LOCAL_IP:$PORT/docs${NC}\n"

echo -e "${YELLOW}Share this URL with your team:${NC}"
echo -e "  ${BLUE}http://$LOCAL_IP:$PORT${NC}\n"

echo -e "${GREEN}Starting server...${NC}\n"

# Activate venv and run server
./venv311/bin/uvicorn app.main:app --host 0.0.0.0 --port $PORT --reload
