#!/bin/bash

# A2A Inspector Setup Script

set -e

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

INSPECTOR_DIR="$HOME/a2a-inspector"

echo -e "${GREEN}=== A2A Inspector Setup ===${NC}\n"

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command -v git &>/dev/null; then
    echo -e "${RED}Error: git is not installed${NC}"
    exit 1
fi

if ! command -v node &>/dev/null; then
    echo -e "${RED}Error: Node.js is not installed${NC}"
    echo "Install from: https://nodejs.org/"
    exit 1
fi

if ! command -v npm &>/dev/null; then
    echo -e "${RED}Error: npm is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}Prerequisites OK${NC}\n"

# Clone repository if not exists
if [ -d "$INSPECTOR_DIR" ]; then
    echo -e "${YELLOW}A2A Inspector already cloned at $INSPECTOR_DIR${NC}"
    echo -e "${YELLOW}Pulling latest changes...${NC}"
    cd "$INSPECTOR_DIR"
    git pull
else
    echo -e "${YELLOW}Cloning A2A Inspector...${NC}"
    git clone https://github.com/a2aproject/a2a-inspector.git "$INSPECTOR_DIR"
    cd "$INSPECTOR_DIR"
fi

# Install backend dependencies
echo -e "\n${YELLOW}Installing backend dependencies...${NC}"
if command -v uv &>/dev/null; then
    uv sync
else
    echo -e "${YELLOW}uv not found, installing with pip...${NC}"
    pip install -e .
fi

# Install frontend dependencies
echo -e "\n${YELLOW}Installing frontend dependencies...${NC}"
cd frontend
npm install

echo -e "\n${GREEN}=== Setup Complete ===${NC}\n"
echo -e "A2A Inspector installed at: ${INSPECTOR_DIR}\n"
echo -e "To run the inspector:\n"
echo -e "  ${YELLOW}cd $INSPECTOR_DIR && bash scripts/run.sh${NC}\n"
echo -e "Or use Docker:\n"
echo -e "  ${YELLOW}cd $INSPECTOR_DIR && docker build -t a2a-inspector . && docker run -p 8080:8080 a2a-inspector${NC}\n"
