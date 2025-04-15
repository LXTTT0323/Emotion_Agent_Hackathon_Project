//
//  LumineaApp.swift
//  Luminea
//
//  Created by thea chen on 2025/4/13.
//

import SwiftUI
import HealthKit

@main
struct LumineaApp: App {
    // 应用级别的HealthStore实例
    private let healthStore = HKHealthStore()
    
    init() {
        // 启动时打印HealthKit是否可用
        if HKHealthStore.isHealthDataAvailable() {
            print("HealthKit在此设备上可用")
        } else {
            print("警告：HealthKit在此设备上不可用")
        }
    }
    
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}
