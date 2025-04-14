# Emotion Agent Hackathon Project

An AI-powered iOS health companion app that offers emotional support based on real-time physiological data from Apple Watch.

## Overview

Emotion Agent targets women aged 22–40 who use Apple Watch. The app analyzes physiological data (heart rate, HRV, sleep, menstrual cycle) alongside text input to provide personalized emotional support and suggestions.

- **Frontend**: iOS app built with Swift/SwiftUI
- **Backend**: Python FastAPI + Semantic Kernel
- **Features**: Emotion classification, personalized suggestions, health data integration

## Project Structure

- **backend/**: FastAPI server with Semantic Kernel
  - **routers/**: API endpoints
  - **services/**: Core logic and tool orchestration
  - **tools/**: Specialized functions for emotion analysis, health data, etc.
  - **memory/**: Contextual memory and user profiles
  - **prompts/**: Templates for LLM interaction
  - **mock_data/**: Sample health data for testing

- **ios-app/**: Swift/SwiftUI iOS application
  - **EmotionAgentApp/**: App source code
  - **Assets/**: Images and resources

- **docs/**: Project documentation
- **tests/**: Test suites

## Setup Instructions

### Quick Start

For your convenience, we've provided scripts to set up and run the backend:

- **On macOS/Linux**: Run `./run_backend.sh` (you may need to add execute permissions with `chmod +x run_backend.sh` first)
- **On Windows**: Run `run_backend.bat` by double-clicking or from the command prompt

These scripts will:
1. Create a virtual environment if needed
2. Install required dependencies
3. Start the backend server

### Manual Backend Setup

If you prefer manual setup:

1. Install Python 3.9+ if not already installed
2. Navigate to the backend directory:
   ```
   cd backend
   ```
3. Install required packages:
   ```
   pip install -r requirements.txt
   ```
4. Run the server:
   ```
   python main.py
   ```
   The API will be available at http://localhost:8000

### iOS App Setup

1. Open the ios-app directory in Xcode
2. Make sure you have the latest Xcode installed
3. Select a simulator or device (preferably an iPhone)
4. Build and run the application

## API Documentation

Once the backend is running, visit http://localhost:8000/docs for the Swagger UI documentation of available endpoints.

## Key Endpoints

- **POST /agent/analyze**: Analyze user text and health data to generate emotional support
- **GET /health/mock_health/{user_id}**: Get mock health data for testing

## Usage Flow

1. User inputs how they're feeling in the iOS app
2. App collects HealthKit data (mocked for now)
3. Data is sent to backend for analysis
4. Backend generates personalized suggestion
5. Response displayed to user in a friendly UI

## Development Roadmap

See [docs/mvp_plan.md](docs/mvp_plan.md) for the development roadmap and milestone plan.

## Testing

Run the tests with:
```
python -m unittest discover tests
```

## License

This project is for demonstration purposes only.
