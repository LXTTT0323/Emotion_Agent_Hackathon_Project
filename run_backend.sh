#!/bin/bash

# Go to the project root directory
cd "$(dirname "$0")"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 could not be found. Please install Python 3 and try again."
    exit 1
fi

# Check if the virtual environment exists, if not create it
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null

# Install requirements
echo "Installing required packages..."
pip install -r backend/requirements.txt

# Run the server
echo "Starting backend server..."
cd backend
python main.py

# Deactivate virtual environment on exit
deactivate 