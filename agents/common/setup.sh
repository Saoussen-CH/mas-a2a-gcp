#!/bin/bash

# Brand Strategist Setup Script
# Sets up the development environment using uv

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=== Brand Strategist Setup ===${NC}\n"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}Installing uv...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
    echo -e "${GREEN}uv installed${NC}\n"
else
    echo -e "${GREEN}uv already installed${NC}\n"
fi

# Create virtual environment
echo -e "${YELLOW}Creating virtual environment...${NC}"
uv venv
echo -e "${GREEN}Virtual environment created${NC}\n"

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source .venv/bin/activate

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
uv pip install -r requirements.txt
echo -e "${GREEN}Dependencies installed${NC}\n"

# Create .env if not exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cp .env.example .env
    echo -e "${GREEN}.env file created - please update with your configuration${NC}\n"
fi

echo -e "${GREEN}=== Setup Complete ===${NC}\n"
echo -e "To activate the environment, run:"
echo -e "  ${YELLOW}source .venv/bin/activate${NC}\n"
echo -e "To start the agent, run:"
echo -e "  ${YELLOW}python agent.py${NC}\n"
echo -e "To run tests, run:"
echo -e "  ${YELLOW}./test_local.sh${NC}\n"
