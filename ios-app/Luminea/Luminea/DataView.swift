import SwiftUI
import HealthKit

struct DataView: View {
    // 健康数据存储
    @State private var heartRate: Double = 0
    @State private var hrv: Double = 0
    @State private var sleepHours: Double = 0
    @State private var stepsCount: Int = 0
    @State private var activeEnergyBurned: Double = 0
    @State private var mindfulMinutes: Int = 0
    @State private var stateOfMind: String = "未记录"  // 新增：情绪状态
    @State private var lastPeriodDate: String = "未记录"  // 新增：上次经期日期
    
    // 健康数据访问状态
    @State private var isAuthorized: Bool = false
    @State private var isLoading: Bool = true
    @State private var errorMessage: String? = nil
    @State private var showingMoodPicker: Bool = false  // 新增：控制情绪选择器显示
    
    // 可选的情绪状态
    private let moodOptions = ["开心", "平静", "疲惫", "焦虑", "伤心", "愤怒", "激动"]
    
    // HealthKit Store
    private let healthStore = HKHealthStore()
    
    // 需要请求的数据类型
    private let typesToRead: Set<HKObjectType> = [
        HKObjectType.quantityType(forIdentifier: .heartRate)!,
        HKObjectType.quantityType(forIdentifier: .heartRateVariabilitySDNN)!,
        HKObjectType.categoryType(forIdentifier: .sleepAnalysis)!,
        HKObjectType.quantityType(forIdentifier: .stepCount)!,
        HKObjectType.quantityType(forIdentifier: .activeEnergyBurned)!,
        HKObjectType.categoryType(forIdentifier: .mindfulSession)!,
        HKObjectType.categoryType(forIdentifier: .menstrualFlow)!  // 新增：经期
    ]
    
    var body: some View {
        ZStack {
            Color.black.ignoresSafeArea()
            
            if isLoading {
                ProgressView()
                    .progressViewStyle(CircularProgressViewStyle(tint: .white))
                    .scaleEffect(1.5)
            } else if let error = errorMessage {
                VStack {
                    Text("无法获取健康数据")
                        .font(.title)
                        .foregroundColor(.white)
                    Text(error)
                        .foregroundColor(.red)
                    Button("重试") {
                        requestHealthData()
                    }
                    .padding()
                    .background(Color.blue)
                    .foregroundColor(.white)
                    .cornerRadius(10)
                }
                .padding()
            } else if !isAuthorized {
                VStack {
                    Text("需要访问健康数据")
                        .font(.title)
                        .foregroundColor(.white)
                    
                    Button("授权健康数据") {
                        requestHealthAuthorization()
                    }
                    .padding()
                    .background(Color.blue)
                    .foregroundColor(.white)
                    .cornerRadius(10)
                }
            } else {
                ScrollView {
                    VStack(spacing: 20) {
                        Text("健康数据")
                            .font(.largeTitle)
                            .fontWeight(.bold)
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .padding(.horizontal)
                        
                        // 心率数据卡片
                        DataCard(title: "心率", value: "\(Int(heartRate))", unit: "BPM", icon: "heart.fill", color: .red)
                        
                        // HRV数据卡片
                        DataCard(title: "心率变异性", value: String(format: "%.1f", hrv), unit: "ms", icon: "waveform.path.ecg", color: .orange)
                        
                        // 睡眠数据卡片
                        DataCard(title: "睡眠时间", value: String(format: "%.1f", sleepHours), unit: "小时", icon: "bed.double.fill", color: .indigo)
                        
                        // 步数数据卡片
                        DataCard(title: "今日步数", value: "\(stepsCount)", unit: "步", icon: "figure.walk", color: .green)
                        
                        // 活动能量数据卡片
                        DataCard(title: "消耗能量", value: String(format: "%.1f", activeEnergyBurned), unit: "卡路里", icon: "flame.fill", color: .orange)
                        
                        // 正念冥想数据卡片
                        DataCard(title: "正念时间", value: "\(mindfulMinutes)", unit: "分钟", icon: "brain.head.profile", color: .purple)
                        
                        // 情绪状态数据卡片
                        DataCard(title: "情绪状态", value: stateOfMind, unit: "", icon: "face.smiling", color: .cyan)
                            .onTapGesture {
                                updateStateOfMind()
                            }
                        
                        // 经期数据卡片
                        DataCard(title: "上次经期", value: lastPeriodDate, unit: "", icon: "calendar", color: .pink)
                        
                        // API数据发送按钮
                        Button(action: sendDataToAPI) {
                            Text("同步数据到服务器")
                                .fontWeight(.semibold)
                                .padding()
                                .frame(maxWidth: .infinity)
                                .background(Color.blue)
                                .foregroundColor(.white)
                                .cornerRadius(10)
                        }
                        .padding(.horizontal)
                        .padding(.top, 10)
                    }
                    .padding(.vertical)
                }
                .sheet(isPresented: $showingMoodPicker) {
                    MoodPickerView(selectedMood: $stateOfMind, isPresented: $showingMoodPicker)
                }
            }
        }
        .onAppear {
            checkHealthAuthorization()
        }
    }
    
    // 检查健康数据授权状态
    private func checkHealthAuthorization() {
        // 确认HealthKit在设备上可用
        guard HKHealthStore.isHealthDataAvailable() else {
            self.errorMessage = "此设备不支持HealthKit"
            self.isLoading = false
            return
        }
        
        // 检查当前授权状态
        healthStore.getRequestStatusForAuthorization(toShare: [], read: typesToRead) { (status, error) in
            DispatchQueue.main.async {
                if status == .unnecessary {
                    // 已授权，直接获取数据
                    self.isAuthorized = true
                    self.requestHealthData()
                } else {
                    // 需要授权
                    self.isAuthorized = false
                    self.isLoading = false
                }
            }
        }
    }
    
    // 请求健康数据授权
    private func requestHealthAuthorization() {
        self.isLoading = true
        
        healthStore.requestAuthorization(toShare: [], read: typesToRead) { success, error in
            DispatchQueue.main.async {
                if success {
                    self.isAuthorized = true
                    self.requestHealthData()
                } else {
                    self.errorMessage = error?.localizedDescription ?? "授权失败"
                    self.isLoading = false
                }
            }
        }
    }
    
    // 获取健康数据
    private func requestHealthData() {
        self.isLoading = true
        self.errorMessage = nil
        
        let group = DispatchGroup()
        
        // 获取心率数据
        group.enter()
        fetchLatestHeartRate { result in
            self.heartRate = result ?? 0
            group.leave()
        }
        
        // 获取HRV数据
        group.enter()
        fetchLatestHRV { result in
            self.hrv = result ?? 0
            group.leave()
        }
        
        // 获取睡眠数据
        group.enter()
        fetchLastNightSleep { result in
            self.sleepHours = result ?? 0
            group.leave()
        }
        
        // 获取步数
        group.enter()
        fetchTodaySteps { result in
            self.stepsCount = result ?? 0
            group.leave()
        }
        
        // 获取活动能量
        group.enter()
        fetchTodayActiveEnergy { result in
            self.activeEnergyBurned = result ?? 0
            group.leave()
        }
        
        // 获取正念冥想时间
        group.enter()
        fetchMindfulMinutes { result in
            self.mindfulMinutes = result ?? 0
            group.leave()
        }
        
        // 获取情绪状态
        group.enter()
        fetchStateOfMind { result in
            self.stateOfMind = result ?? "未记录"
            group.leave()
        }
        
        // 获取经期数据
        group.enter()
        fetchLastPeriodDate { result in
            self.lastPeriodDate = result ?? "未记录"
            group.leave()
        }
        
        // 所有数据获取完成后更新UI
        group.notify(queue: .main) {
            self.isLoading = false
        }
    }
    
    // 获取最新心率
    private func fetchLatestHeartRate(completion: @escaping (Double?) -> Void) {
        guard let heartRateType = HKObjectType.quantityType(forIdentifier: .heartRate) else {
            completion(nil)
            return
        }
        
        let predicate = HKQuery.predicateForSamples(withStart: Calendar.current.date(byAdding: .day, value: -1, to: Date()), end: Date(), options: .strictEndDate)
        let sortDescriptor = NSSortDescriptor(key: HKSampleSortIdentifierEndDate, ascending: false)
        
        let query = HKSampleQuery(sampleType: heartRateType, predicate: predicate, limit: 1, sortDescriptors: [sortDescriptor]) { (_, samples, error) in
            guard error == nil, let sample = samples?.first as? HKQuantitySample else {
                completion(nil)
                return
            }
            
            let heartRate = sample.quantity.doubleValue(for: HKUnit.count().unitDivided(by: .minute()))
            completion(heartRate)
        }
        
        healthStore.execute(query)
    }
    
    // 获取最新HRV
    private func fetchLatestHRV(completion: @escaping (Double?) -> Void) {
        guard let hrvType = HKObjectType.quantityType(forIdentifier: .heartRateVariabilitySDNN) else {
            completion(nil)
            return
        }
        
        let predicate = HKQuery.predicateForSamples(withStart: Calendar.current.date(byAdding: .day, value: -1, to: Date()), end: Date(), options: .strictEndDate)
        let sortDescriptor = NSSortDescriptor(key: HKSampleSortIdentifierEndDate, ascending: false)
        
        let query = HKSampleQuery(sampleType: hrvType, predicate: predicate, limit: 1, sortDescriptors: [sortDescriptor]) { (_, samples, error) in
            guard error == nil, let sample = samples?.first as? HKQuantitySample else {
                completion(nil)
                return
            }
            
            let hrv = sample.quantity.doubleValue(for: HKUnit.secondUnit(with: .milli))
            completion(hrv)
        }
        
        healthStore.execute(query)
    }
    
    // 获取昨晚睡眠时间
    private func fetchLastNightSleep(completion: @escaping (Double?) -> Void) {
        guard let sleepType = HKObjectType.categoryType(forIdentifier: .sleepAnalysis) else {
            completion(nil)
            return
        }
        
        // 获取昨天的日期
        let calendar = Calendar.current
        let now = Date()
        let yesterday = calendar.date(byAdding: .day, value: -1, to: now)!
        let startOfYesterday = calendar.startOfDay(for: yesterday)
        let endOfDay = calendar.date(byAdding: .day, value: 1, to: startOfYesterday)!
        
        let predicate = HKQuery.predicateForSamples(withStart: startOfYesterday, end: endOfDay, options: .strictStartDate)
        
        let query = HKSampleQuery(sampleType: sleepType, predicate: predicate, limit: HKObjectQueryNoLimit, sortDescriptors: nil) { (_, samples, error) in
            guard error == nil, let samples = samples as? [HKCategorySample] else {
                completion(nil)
                return
            }
            
            var totalSleepTime: TimeInterval = 0
            
            for sample in samples {
                if sample.value == HKCategoryValueSleepAnalysis.asleepUnspecified.rawValue || 
                   sample.value == HKCategoryValueSleepAnalysis.asleepCore.rawValue || 
                   sample.value == HKCategoryValueSleepAnalysis.asleepDeep.rawValue || 
                   sample.value == HKCategoryValueSleepAnalysis.asleepREM.rawValue {
                    let sleepTime = sample.endDate.timeIntervalSince(sample.startDate)
                    totalSleepTime += sleepTime
                }
            }
            
            // 转换为小时
            let sleepHours = totalSleepTime / 3600.0
            completion(sleepHours)
        }
        
        healthStore.execute(query)
    }
    
    // 获取今日步数
    private func fetchTodaySteps(completion: @escaping (Int?) -> Void) {
        guard let stepType = HKObjectType.quantityType(forIdentifier: .stepCount) else {
            completion(nil)
            return
        }
        
        let calendar = Calendar.current
        let now = Date()
        let startOfDay = calendar.startOfDay(for: now)
        
        let predicate = HKQuery.predicateForSamples(withStart: startOfDay, end: now, options: .strictStartDate)
        
        let query = HKStatisticsQuery(quantityType: stepType, quantitySamplePredicate: predicate, options: .cumulativeSum) { (_, result, error) in
            guard error == nil, let result = result, let sum = result.sumQuantity() else {
                completion(nil)
                return
            }
            
            let steps = Int(sum.doubleValue(for: HKUnit.count()))
            completion(steps)
        }
        
        healthStore.execute(query)
    }
    
    // 获取今日活动能量消耗
    private func fetchTodayActiveEnergy(completion: @escaping (Double?) -> Void) {
        guard let energyType = HKObjectType.quantityType(forIdentifier: .activeEnergyBurned) else {
            completion(nil)
            return
        }
        
        let calendar = Calendar.current
        let now = Date()
        let startOfDay = calendar.startOfDay(for: now)
        
        let predicate = HKQuery.predicateForSamples(withStart: startOfDay, end: now, options: .strictStartDate)
        
        let query = HKStatisticsQuery(quantityType: energyType, quantitySamplePredicate: predicate, options: .cumulativeSum) { (_, result, error) in
            guard error == nil, let result = result, let sum = result.sumQuantity() else {
                completion(nil)
                return
            }
            
            let calories = sum.doubleValue(for: HKUnit.kilocalorie())
            completion(calories)
        }
        
        healthStore.execute(query)
    }
    
    // 获取正念冥想时间
    private func fetchMindfulMinutes(completion: @escaping (Int?) -> Void) {
        guard let mindfulType = HKObjectType.categoryType(forIdentifier: .mindfulSession) else {
            completion(nil)
            return
        }
        
        let calendar = Calendar.current
        let now = Date()
        let startOfDay = calendar.startOfDay(for: now)
        
        let predicate = HKQuery.predicateForSamples(withStart: startOfDay, end: now, options: .strictStartDate)
        
        let query = HKSampleQuery(sampleType: mindfulType, predicate: predicate, limit: HKObjectQueryNoLimit, sortDescriptors: nil) { (_, samples, error) in
            guard error == nil, let samples = samples else {
                completion(nil)
                return
            }
            
            var totalMindfulTime: TimeInterval = 0
            
            for sample in samples {
                let mindfulTime = sample.endDate.timeIntervalSince(sample.startDate)
                totalMindfulTime += mindfulTime
            }
            
            let mindfulMinutes = Int(totalMindfulTime / 60.0)
            completion(mindfulMinutes)
        }
        
        healthStore.execute(query)
    }
    
    // 获取情绪状态
    private func fetchStateOfMind(completion: @escaping (String?) -> Void) {
        // 注意：HealthKit没有直接的情绪状态类别
        // 这里我们模拟一个简单的情绪状态获取方法
        // 在实际应用中，您可能需要从自己的数据存储或其他服务获取情绪状态
        
        // 假设我们有自定义的情绪数据存储
        let userDefaults = UserDefaults.standard
        if let savedMood = userDefaults.string(forKey: "userMoodState") {
            completion(savedMood)
        } else {
            // 如果没有保存的情绪状态，返回一个默认值或根据其他健康指标推断
            if self.heartRate > 90 {
                completion("激动")
            } else if self.sleepHours < 6 {
                completion("疲惫")
            } else if self.mindfulMinutes > 30 {
                completion("平静")
            } else {
                completion("普通")
            }
        }
    }
    
    // 获取经期数据
    private func fetchLastPeriodDate(completion: @escaping (String?) -> Void) {
        guard let menstrualType = HKObjectType.categoryType(forIdentifier: .menstrualFlow) else {
            completion(nil)
            return
        }
        
        // 获取过去3个月的经期数据
        let calendar = Calendar.current
        let now = Date()
        let threeMonthsAgo = calendar.date(byAdding: .month, value: -3, to: now)!
        
        let predicate = HKQuery.predicateForSamples(withStart: threeMonthsAgo, end: now, options: .strictEndDate)
        let sortDescriptor = NSSortDescriptor(key: HKSampleSortIdentifierEndDate, ascending: false)
        
        let query = HKSampleQuery(sampleType: menstrualType, predicate: predicate, limit: 10, sortDescriptors: [sortDescriptor]) { (_, samples, error) in
            guard error == nil, let samples = samples as? [HKCategorySample], !samples.isEmpty else {
                completion(nil)
                return
            }
            
            // 获取最近的一次经期记录
            if let lastPeriod = samples.first {
                let dateFormatter = DateFormatter()
                dateFormatter.dateStyle = .medium
                dateFormatter.timeStyle = .none
                dateFormatter.locale = Locale(identifier: "zh_CN")
                
                let dateString = dateFormatter.string(from: lastPeriod.startDate)
                completion(dateString)
            } else {
                completion(nil)
            }
        }
        
        healthStore.execute(query)
    }
    
    // 发送数据到API
    private func sendDataToAPI() {
        // 构建要发送的数据
        let healthData: [String: Any] = [
            "heartRate": heartRate,
            "heartRateVariability": hrv,
            "sleepHours": sleepHours,
            "steps": stepsCount,
            "activeEnergyBurned": activeEnergyBurned,
            "mindfulMinutes": mindfulMinutes,
            "stateOfMind": stateOfMind,
            "lastPeriodDate": lastPeriodDate,
            "timestamp": Date().timeIntervalSince1970,
            "userId": "用户ID" // 需要从设置或登录状态获取
        ]
        
        // 设置Azure API端点
        guard let url = URL(string: "https://luminea-cheme6cpfhbvf7e6.australiacentral-01.azurewebsites.net/api/health-data") else {
            print("无效的API URL")
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")
        // 添加身份验证令牌（如果有）
        // request.addValue("Bearer \(userToken)", forHTTPHeaderField: "Authorization")
        
        do {
            request.httpBody = try JSONSerialization.data(withJSONObject: healthData)
            
            // 显示加载指示器
            let loadingIndicator = UIActivityIndicatorView(style: .medium)
            loadingIndicator.startAnimating()
            
            URLSession.shared.dataTask(with: request) { data, response, error in
                // 主线程更新UI
                DispatchQueue.main.async {
                    loadingIndicator.stopAnimating()
                    
                    if let error = error {
                        // 处理错误情况
                        print("数据发送失败: \(error.localizedDescription)")
                        // 这里可以添加错误提示UI
                        return
                    }
                    
                    guard let httpResponse = response as? HTTPURLResponse else {
                        print("无响应")
                        return
                    }
                    
                    if (200...299).contains(httpResponse.statusCode) {
                        // 成功处理
                        print("数据发送成功，状态码: \(httpResponse.statusCode)")
                        // 这里可以添加成功提示UI
                    } else {
                        // 处理HTTP错误
                        print("服务器错误，状态码: \(httpResponse.statusCode)")
                        // 这里可以添加错误提示UI
                    }
                }
            }.resume()
        } catch {
            print("数据编码错误: \(error)")
        }
    }
    
    // 更新情绪状态
    private func updateStateOfMind() {
        showingMoodPicker = true
    }
}

// 数据卡片组件
struct DataCard: View {
    var title: String
    var value: String
    var unit: String
    var icon: String
    var color: Color
    
    var body: some View {
        VStack {
            HStack {
                Image(systemName: icon)
                    .font(.title)
                    .foregroundColor(color)
                
                Text(title)
                    .font(.headline)
                    .foregroundColor(.white)
                
                Spacer()
            }
            
            HStack {
                Text(value)
                    .font(.system(size: 30, weight: .bold))
                    .foregroundColor(.white)
                
                Text(unit)
                    .font(.body)
                    .foregroundColor(.gray)
                
                Spacer()
            }
        }
        .padding()
        .background(Color.gray.opacity(0.2))
        .cornerRadius(15)
        .padding(.horizontal)
    }
}

// 情绪选择器视图
struct MoodPickerView: View {
    @Binding var selectedMood: String
    @Binding var isPresented: Bool
    
    // 可选的情绪状态
    private let moodOptions = ["开心", "平静", "疲惫", "焦虑", "伤心", "愤怒", "激动"]
    
    var body: some View {
        NavigationView {
            List {
                ForEach(moodOptions, id: \.self) { mood in
                    Button(action: {
                        selectedMood = mood
                        // 保存到UserDefaults
                        UserDefaults.standard.set(mood, forKey: "userMoodState")
                        isPresented = false
                    }) {
                        HStack {
                            Text(mood)
                                .foregroundColor(.primary)
                            Spacer()
                            if selectedMood == mood {
                                Image(systemName: "checkmark")
                                    .foregroundColor(.blue)
                            }
                        }
                    }
                }
            }
            .navigationTitle("选择当前情绪")
            .navigationBarItems(trailing: Button("取消") {
                isPresented = false
            })
        }
    }
} 