import SwiftUI

// 枚举定义情绪类型及其属性（颜色、图标）
enum EmotionType: String, CaseIterable {
    case calm = "🙂"
    case happy = "😊"
    case excited = "🤩"
    case anxious = "😟"
    case sad = "😢"
    case wronged = "😣"
    case angry = "😡"
    case unknown = "😶"

    var name: String {
        switch self {
        case .calm: return "平静"
        case .happy: return "愉悦"
        case .excited: return "兴奋"
        case .anxious: return "焦虑"
        case .sad: return "悲伤"
        case .wronged: return "委屈"
        case .angry: return "生气"
        case .unknown: return "未知"
        }
    }

    var color: Color {
        switch self {
        case .calm: return Color(hex: "#3498DB")
        case .happy: return Color(hex: "#34C759")
        case .excited: return Color(hex: "#00BFFF")
        case .anxious: return Color(hex: "#FF9500")
        case .sad: return Color(hex: "#8E8E93")
        case .wronged: return Color(hex: "#AF52DE")
        case .angry: return Color(hex: "#FF3B30")
        case .unknown: return Color(hex: "#C7C7CC")
        }
    }
}

struct EmotionView: View {
    @State private var currentEmotion: EmotionType = .calm
    @State private var showSelector = false
    @State private var summaryText: String = "正在获取今日情绪总结..."

    let emotionRatios: [(EmotionType, Int)] = [
        (.calm, 25),
        (.excited, 15),
        (.happy, 10)
    ]

    var body: some View {
        ZStack {
            Color.black.ignoresSafeArea()
            EmotionStarField(emotionRatios: emotionRatios).ignoresSafeArea()

            ScrollView(showsIndicators: false) {
                VStack(spacing: 24) {
                    VStack(spacing: 8) {
                        Text("情绪状态")
                            .font(.system(size: 24, weight: .semibold))
                            .foregroundColor(.white)
                        Text("今晚你好呀，感觉还好吗？")
                            .font(.subheadline)
                            .foregroundColor(.white.opacity(0.8))
                    }
                    .padding(.top, 60)

                    // 量子态情绪星云模块（放在顶部下方）
                    EmotionNebulaView(emotion: currentEmotion)
                        .frame(height: 200)
                        .padding(.horizontal)

                    // 今日总结
                    VStack(alignment: .leading, spacing: 12) {
                        Text("🧾 今日总结")
                            .font(.headline)
                            .foregroundColor(.white)
                        Text(summaryText)
                            .font(.body)
                            .foregroundColor(.white.opacity(0.9))
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .padding()
                            .background(Color.white.opacity(0.05))
                            .cornerRadius(12)
                    }
                    .padding(.horizontal)
                    .task {
                        // 模拟异步获取总结（将来由 AI Agent 返回）
                        try? await Task.sleep(nanoseconds: 1_000_000_000)
                        summaryText = "你今天处于平静状态 68%，整体情绪稳定。"
                    }

                    // Recommended Interventions 功能卡片区块
                    VStack(alignment: .leading, spacing: 16) {
                        Text("🧘‍♂️ Recommended Interventions")
                            .font(.headline)
                            .foregroundColor(.white)

                        VStack(spacing: 16) {
                            HStack(spacing: 16) {
                                InterveneCard(icon: "🧘‍♀️", title: "Breathing")
                                InterveneCard(icon: "🎵", title: "Calm Music")
                            }
                            HStack(spacing: 16) {
                                InterveneCard(icon: "📝", title: "Journaling")
                                InterveneCard(icon: "🧠", title: "AI Chat")
                            }
                        }
                        .padding()
                        .background(
                            LinearGradient(
                                gradient: Gradient(colors: [Color(hex: "#001F3F"), Color(hex: "#001A33")]),
                                startPoint: .top,
                                endPoint: .bottom
                            )
                        )
                        .cornerRadius(20)
                    }
                    .padding(.horizontal, 20)
                    .padding(.bottom, 40)
                }
                .frame(maxWidth: .infinity)
            }

            if showSelector {
                EmotionSelectorView(currentEmotion: $currentEmotion, isPresented: $showSelector)
                    .transition(.opacity)
            }
        }
    }
}


struct EmotionStarField: View {
    let emotionRatios: [(EmotionType, Int)]

    var body: some View {
        ZStack {
            ForEach(0..<emotionRatios.count, id: \ .self) { index in
                let (emotion, count) = emotionRatios[index]
                ForEach(0..<count, id: \ .self) { _ in
                    Circle()
                        .fill(emotion.color.opacity(Double.random(in: 0.4...0.8)))
                        .frame(width: 2.5, height: 2.5)
                        .position(
                            x: CGFloat.random(in: 0...UIScreen.main.bounds.width),
                            y: CGFloat.random(in: 0...UIScreen.main.bounds.height)
                        )
                        .opacity(Double.random(in: 0.6...1))
                        .animation(
                            Animation.easeInOut(duration: Double.random(in: 1.5...3)).repeatForever(autoreverses: true),
                            value: UUID()
                        )
                }
            }
        }
    }
}




// 模拟“情绪呼吸”星云动画视图
struct EmotionNebulaView: View {
    let emotion: EmotionType
    @State private var scale: CGFloat = 1.0
    @State private var opacity: Double = 0.6

    var body: some View {
        ZStack {
            ForEach(0..<25, id: \ .self) { _ in
                Circle()
                    .fill(emotion.color.opacity(0.5))
                    .frame(width: CGFloat.random(in: 4...10))
                    .position(
                        x: CGFloat.random(in: 0...UIScreen.main.bounds.width - 40),
                        y: CGFloat.random(in: 0...180)
                    )
            }
        }
        .scaleEffect(scale)
        .opacity(opacity)
        .onAppear {
            withAnimation(.easeInOut(duration: emotion == .anxious ? 1 : 3).repeatForever(autoreverses: true)) {
                scale = emotion == .anxious ? 1.3 : 1.1
                opacity = 0.9
            }
        }
    }
}

struct InterveneCard: View {
    let icon: String
    let title: String

    var body: some View {
        VStack(spacing: 8) {
            Text(icon)
                .font(.system(size: 28))
            Text(title)
                .font(.body)
                .foregroundColor(.white.opacity(0.9))
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(Color.white.opacity(0.05))
        .cornerRadius(12)
    }
}

extension Color {
    init(hex: String) {
        let scanner = Scanner(string: hex)
        _ = scanner.scanString("#")
        var rgb: UInt64 = 0
        scanner.scanHexInt64(&rgb)
        let r = Double((rgb >> 16) & 0xFF) / 255
        let g = Double((rgb >> 8) & 0xFF) / 255
        let b = Double(rgb & 0xFF) / 255
        self.init(red: r, green: g, blue: b)
    }
}
