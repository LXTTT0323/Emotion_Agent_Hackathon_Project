import SwiftUI

struct ContentView: View {
    @StateObject private var healthManager = HealthManager()
    @State private var userInput: String = ""
    @State private var agentResponse: AgentResponse?
    @State private var isLoading: Bool = false
    
    // Hardcoded user ID for demo purposes
    private let userId = "user123"
    
    var body: some View {
        VStack {
            // Header
            Text("Emotion Agent")
                .font(.largeTitle)
                .fontWeight(.bold)
                .padding()
                .foregroundColor(.indigo)
            
            // Health data summary (simplified)
            healthDataSummaryView
            
            // Chat interaction area
            chatAreaView
            
            // Input area
            userInputView
        }
        .padding()
        .onAppear {
            // Request health data access when app appears
            healthManager.requestAuthorization()
        }
    }
    
    // Health data summary view
    private var healthDataSummaryView: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Health Summary")
                .font(.headline)
            
            if let healthData = healthManager.healthData {
                HStack {
                    healthMetricView(
                        icon: "heart.fill",
                        value: "\(healthData.heartRate?.avg ?? 0)",
                        unit: "bpm",
                        color: .red
                    )
                    
                    healthMetricView(
                        icon: "waveform.path.ecg",
                        value: "\(healthData.hrv?.rmssd ?? 0)",
                        unit: "ms",
                        color: .orange
                    )
                    
                    healthMetricView(
                        icon: "bed.double.fill",
                        value: "\(healthData.sleep?.totalMinutes ?? 0)",
                        unit: "min",
                        color: .blue
                    )
                }
            } else {
                Text("Loading health data...")
                    .foregroundColor(.secondary)
                    .padding(.vertical, 4)
            }
        }
        .padding()
        .background(Color.gray.opacity(0.1))
        .cornerRadius(12)
    }
    
    // Individual health metric view
    private func healthMetricView(icon: String, value: String, unit: String, color: Color) -> some View {
        VStack {
            Image(systemName: icon)
                .foregroundColor(color)
                .font(.title2)
            Text(value)
                .font(.headline)
            Text(unit)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity)
    }
    
    // Chat area view
    private var chatAreaView: some View {
        VStack {
            if let response = agentResponse {
                // Agent response card
                VStack(alignment: .leading, spacing: 8) {
                    HStack {
                        Text("Emotion Agent")
                            .font(.headline)
                        Spacer()
                        emotionBadge(emotion: response.emotion)
                    }
                    
                    Text(response.suggestion)
                        .padding(.vertical, 4)
                }
                .padding()
                .background(Color.purple.opacity(0.1))
                .cornerRadius(12)
            } else if isLoading {
                ProgressView("Analyzing...")
                    .padding()
            } else {
                // Placeholder when no responses
                Text("Share how you're feeling, and I'll provide personalized support.")
                    .foregroundColor(.secondary)
                    .multilineTextAlignment(.center)
                    .padding()
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
    
    // User input view
    private var userInputView: some View {
        HStack {
            TextField("How are you feeling?", text: $userInput)
                .padding()
                .background(Color.gray.opacity(0.1))
                .cornerRadius(12)
            
            Button(action: sendMessage) {
                Image(systemName: "arrow.up.circle.fill")
                    .foregroundColor(.purple)
                    .font(.title)
            }
            .disabled(userInput.isEmpty || isLoading)
        }
    }
    
    // Emotion badge view
    private func emotionBadge(emotion: String) -> some View {
        let color: Color = {
            switch emotion.lowercased() {
            case "happy": return .green
            case "sad": return .blue
            case "angry": return .red
            case "anxious": return .orange
            case "tired": return .gray
            default: return .purple
            }
        }()
        
        return Text(emotion.capitalized)
            .font(.caption)
            .padding(.horizontal, 8)
            .padding(.vertical, 4)
            .background(color.opacity(0.2))
            .foregroundColor(color)
            .cornerRadius(8)
    }
    
    // Send message function
    private func sendMessage() {
        guard !userInput.isEmpty else { return }
        
        let inputText = userInput
        userInput = ""
        isLoading = true
        
        // Create agent client
        let client = AgentClient()
        
        // Send request to backend
        Task {
            do {
                let response = try await client.analyze(
                    userId: userId,
                    text: inputText,
                    healthData: healthManager.healthData
                )
                
                // Update UI on main thread
                DispatchQueue.main.async {
                    self.agentResponse = response
                    self.isLoading = false
                }
            } catch {
                print("Error: \(error)")
                
                // Update UI on main thread
                DispatchQueue.main.async {
                    // For demo, create a fallback response
                    self.agentResponse = AgentResponse(
                        suggestion: "I'm having trouble connecting right now. Please try again in a moment.",
                        emotion: "neutral",
                        confidence: 0.5
                    )
                    self.isLoading = false
                }
            }
        }
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
} 