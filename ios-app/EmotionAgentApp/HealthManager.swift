import Foundation
import HealthKit

class HealthManager: ObservableObject {
    private let healthStore = HKHealthStore()
    @Published var healthData: HealthData?
    
    // Types of health data to request
    private let typesToRead: Set<HKObjectType> = {
        guard
            let heartRate = HKObjectType.quantityType(forIdentifier: .heartRate),
            let hrv = HKObjectType.quantityType(forIdentifier: .heartRateVariabilitySDNN),
            let sleepAnalysis = HKObjectType.categoryType(forIdentifier: .sleepAnalysis),
            let steps = HKObjectType.quantityType(forIdentifier: .stepCount)
        else {
            fatalError("These types should be available on all iOS devices")
        }
        
        return [heartRate, hrv, sleepAnalysis, steps]
    }()
    
    init() {
        // In a real app, we'd request authorization and fetch data right away
        // For the demo, we'll use mock data by default
        loadMockHealthData()
    }
    
    func requestAuthorization() {
        // Check if HealthKit is available on this device
        guard HKHealthStore.isHealthDataAvailable() else {
            print("HealthKit is not available on this device")
            return
        }
        
        // Request authorization to access health data
        healthStore.requestAuthorization(toShare: nil, read: typesToRead) { success, error in
            if let error = error {
                print("Error requesting HealthKit authorization: \(error)")
                return
            }
            
            if success {
                print("HealthKit authorization granted")
                DispatchQueue.main.async {
                    // For demo, we'll still use mock data
                    // In a real app, we'd fetch actual data here
                    self.loadMockHealthData()
                }
            } else {
                print("HealthKit authorization denied")
            }
        }
    }
    
    // In a real app, this would fetch actual data from HealthKit
    private func fetchHealthData() {
        // For simplicity, we'll just load mock data
        loadMockHealthData()
        
        // In a real implementation, this would:
        // 1. Fetch heart rate data (average, min, max)
        // 2. Fetch HRV data
        // 3. Fetch sleep data
        // 4. Fetch step count
        // 5. Process and update the published healthData property
    }
    
    // Load mock health data for the demo
    private func loadMockHealthData() {
        DispatchQueue.main.async {
            self.healthData = HealthData(
                heartRate: HeartRateData(
                    avg: 72,
                    min: 58,
                    max: 112,
                    resting: 65
                ),
                hrv: HRVData(
                    rmssd: 42.8,
                    sdnn: 51.3
                ),
                sleep: SleepData(
                    deepSleepMinutes: 85,
                    remSleepMinutes: 110,
                    lightSleepMinutes: 210,
                    totalMinutes: 405
                ),
                steps: StepsData(
                    count: 7850,
                    goal: 10000
                ),
                menstrualCycle: MenstrualCycleData(
                    phase: "follicular",
                    day: 8
                )
            )
        }
    }
}

// MARK: - Data Models

struct HealthData: Codable {
    var heartRate: HeartRateData?
    var hrv: HRVData?
    var sleep: SleepData?
    var steps: StepsData?
    var menstrualCycle: MenstrualCycleData?
    var timestamp: Date = Date()
}

struct HeartRateData: Codable {
    var avg: Int
    var min: Int
    var max: Int
    var resting: Int
}

struct HRVData: Codable {
    var rmssd: Double
    var sdnn: Double
}

struct SleepData: Codable {
    var deepSleepMinutes: Int
    var remSleepMinutes: Int
    var lightSleepMinutes: Int
    var totalMinutes: Int
}

struct StepsData: Codable {
    var count: Int
    var goal: Int
}

struct MenstrualCycleData: Codable {
    var phase: String
    var day: Int
} 