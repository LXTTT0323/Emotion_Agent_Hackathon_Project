## Emotion Agent – System Overview

Emotion Agent is a cross-platform AI app designed to provide contextual emotional support based on real-time physiological data from Apple Watch.

- **Frontend**: iOS app (SwiftUI) that collects user input and health metrics.
- **Backend**: Python FastAPI + Semantic Kernel handles logic, memory, and response generation.
- **Privacy-first**: Health data stays local when possible. Agent memory stored on device unless sync is requested.

### Architecture Components

#### iOS App
- **ContentView.swift**: Main UI with chat interface and health data display
- **HealthManager.swift**: Handles HealthKit access and data processing
- **AgentClient.swift**: Communicates with the backend API

#### Backend Server
- **FastAPI Framework**: Provides API endpoints and request handling
- **Semantic Kernel**: Orchestrates AI tools and prompt templates
- **Memory System**: Maintains conversation context and emotion history
- **Tools**: Specialized functions for emotion analysis, health data processing, etc.

### Data Flow

1. User inputs text on iOS app
2. App collects recent health data via HealthKit
3. Both are sent to the backend `/agent/analyze` endpoint
4. Backend:
   - Analyzes emotion in the text
   - Retrieves user profile preferences
   - Considers health metrics and patterns
   - Generates personalized suggestion via prompt template
   - Records interaction in memory
5. Response is returned to iOS app and displayed to user

### Key Features

- **Emotion Classification**: Identifies the user's emotional state from text
- **Physiological Context**: Incorporates health data to better understand the user's state
- **Personalized Support**: Tailored suggestions based on user preferences
- **Contextual Memory**: Remembers past interactions and emotion patterns
- **Privacy-Focused**: Minimizes data transfer and stores sensitive data locally

### Technologies

- **Swift/SwiftUI**: iOS app development
- **HealthKit**: Access to Apple Watch health metrics
- **Python/FastAPI**: Backend API server
- **Semantic Kernel**: AI orchestration framework
- **JSON**: Data exchange format between components 