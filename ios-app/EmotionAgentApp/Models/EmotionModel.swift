import Foundation
import SwiftUI

// MARK: - Emotion Types

enum EmotionType: String, Codable, CaseIterable {
    case happy
    case sad
    case angry
    case anxious
    case tired
    case neutral
    
    var label: String {
        switch self {
        case .happy: return "Happy"
        case .sad: return "Sad"
        case .angry: return "Angry"
        case .anxious: return "Anxious"
        case .tired: return "Tired"
        case .neutral: return "Neutral"
        }
    }
    
    var color: Color {
        switch self {
        case .happy: return .green
        case .sad: return .blue
        case .angry: return .red
        case .anxious: return .orange
        case .tired: return .gray
        case .neutral: return .purple
        }
    }
    
    var icon: String {
        switch self {
        case .happy: return "face.smiling"
        case .sad: return "cloud.rain"
        case .angry: return "flame"
        case .anxious: return "waveform.path.ecg"
        case .tired: return "bed.double"
        case .neutral: return "face.dashed"
        }
    }
    
    // Helper to convert string to emotion type
    static func from(string: String) -> EmotionType {
        return EmotionType.allCases.first { $0.rawValue == string.lowercased() } ?? .neutral
    }
}

// MARK: - Emotion History

struct EmotionHistoryEntry: Identifiable, Codable {
    let id = UUID()
    let timestamp: Date
    let emotion: String
    
    var emotionType: EmotionType {
        return EmotionType.from(string: emotion)
    }
}

// MARK: - Emotion Log (for future visualization)

class EmotionLog: ObservableObject {
    @Published var entries: [EmotionHistoryEntry] = []
    
    func addEntry(emotion: String) {
        let entry = EmotionHistoryEntry(timestamp: Date(), emotion: emotion)
        entries.append(entry)
        
        // Keep the log at a reasonable size
        if entries.count > 50 {
            entries.removeFirst(entries.count - 50)
        }
    }
} 