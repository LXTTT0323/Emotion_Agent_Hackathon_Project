import Foundation

// MARK: - API Models

struct AnalysisRequest: Codable {
    let userId: String
    let text: String
    let healthData: HealthData?
}

struct AgentResponse: Codable {
    let suggestion: String
    let emotion: String
    let confidence: Double
}

// MARK: - Agent Client

class AgentClient {
    // In a real app, this would be configured from a settings file or environment
    private let apiBaseURL = "http://localhost:8000"
    
    func analyze(userId: String, text: String, healthData: HealthData?) async throws -> AgentResponse {
        // In a real implementation, we would send a request to the backend
        // For demo purposes, we'll simulate a network delay and return a mock response
        
        // Simulate network delay
        try await Task.sleep(nanoseconds: 1_000_000_000) // 1 second delay
        
        // For a real implementation, uncomment this code:
        /*
        guard let url = URL(string: "\(apiBaseURL)/agent/analyze") else {
            throw AgentError.invalidURL
        }
        
        let request = AnalysisRequest(
            userId: userId,
            text: text,
            healthData: healthData
        )
        
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.addValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.httpBody = try JSONEncoder().encode(request)
        
        let (data, response) = try await URLSession.shared.data(for: urlRequest)
        
        guard let httpResponse = response as? HTTPURLResponse,
              (200...299).contains(httpResponse.statusCode) else {
            throw AgentError.serverError
        }
        
        return try JSONDecoder().decode(AgentResponse.self, from: data)
        */
        
        // Mock response based on text content
        return generateMockResponse(for: text)
    }
    
    // Generate a mock response based on text keywords for demo purposes
    private func generateMockResponse(for text: String) -> AgentResponse {
        let lowercasedText = text.lowercased()
        
        // Simple emotion detection based on keywords
        if lowercasedText.contains("happy") || lowercasedText.contains("good") || lowercasedText.contains("great") {
            return AgentResponse(
                suggestion: "It's wonderful that you're feeling positive! This is a good time to engage in activities you enjoy and connect with others.",
                emotion: "happy",
                confidence: 0.85
            )
        } else if lowercasedText.contains("sad") || lowercasedText.contains("down") || lowercasedText.contains("blue") {
            return AgentResponse(
                suggestion: "I notice you might be feeling down. Taking a few moments for self-care like a warm drink or gentle movement could help lift your mood.",
                emotion: "sad",
                confidence: 0.82
            )
        } else if lowercasedText.contains("stress") || lowercasedText.contains("anxious") || lowercasedText.contains("worry") {
            return AgentResponse(
                suggestion: "I can see you're feeling stressed. Taking a few deep breaths and practicing the 5-4-3-2-1 grounding technique might help center you.",
                emotion: "anxious",
                confidence: 0.88
            )
        } else if lowercasedText.contains("tired") || lowercasedText.contains("exhausted") || lowercasedText.contains("sleep") {
            return AgentResponse(
                suggestion: "Your body might need rest. Honoring that need with a short break or early bedtime tonight could help restore your energy.",
                emotion: "tired",
                confidence: 0.80
            )
        } else if lowercasedText.contains("angry") || lowercasedText.contains("frustrated") || lowercasedText.contains("mad") {
            return AgentResponse(
                suggestion: "I sense frustration in your message. Taking a moment to step back and write down what's bothering you might help process these feelings.",
                emotion: "angry",
                confidence: 0.75
            )
        } else {
            // Default response if emotion is unclear
            return AgentResponse(
                suggestion: "Thank you for sharing. Taking a moment for mindfulness might help you connect with how you're feeling right now.",
                emotion: "neutral",
                confidence: 0.60
            )
        }
    }
}

// MARK: - Errors

enum AgentError: Error {
    case invalidURL
    case serverError
    case decodingError
} 