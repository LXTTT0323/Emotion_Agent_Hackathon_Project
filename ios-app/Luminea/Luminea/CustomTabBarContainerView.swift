import SwiftUI

struct CustomTabBarContainerView: View {
    @State private var selectedIndex = 0

    var body: some View {
        ZStack(alignment: .bottom) {
            TabView(selection: $selectedIndex) {
                EmotionView()
                    .tag(0)
                TrendsView()
                    .tag(1)
                DataView()
                    .tag(2)
                SettingsView()
                    .tag(3)
            }
            .tabViewStyle(.page(indexDisplayMode: .never)) // 去除系统 Tab 样式
            
            CustomTabBar(selectedIndex: $selectedIndex)
        }
        .ignoresSafeArea(edges: .bottom)
    }
}
struct TrendsView: View {
    var body: some View {
        ZStack {
            Color.black.ignoresSafeArea()
            Text("Trends 页面")
                .foregroundColor(.white)
        }
    }
}

struct SettingsView: View {
    var body: some View {
        ZStack {
            Color.black.ignoresSafeArea()
            Text("Settings 页面")
                .foregroundColor(.white)
        }
    }
}
