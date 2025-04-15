//
//  CustomTabBar.swift
//  Luminea
//
//  Created by thea chen on 2025/4/13.
//

import SwiftUICore
import SwiftUI

struct CustomTabBar: View {
    @Binding var selectedIndex: Int

    let icons = [
        ("sparkle", "Emotions"),
        ("chart.xyaxis.line", "Trends"),
        ("waveform.path.ecg", "Data"),
        ("gearshape", "Settings")
    ]

    var body: some View {
        HStack {
            ForEach(0..<icons.count, id: \.self) { i in
                Button(action: {
                    selectedIndex = i
                }) {
                    VStack(spacing: 4) {
                        Image(systemName: icons[i].0)
                            .font(.system(size: 20))
                            .foregroundColor(selectedIndex == i ? Color(hex: "#00FF7F") : Color.white.opacity(0.7))
                        Text(icons[i].1)
                            .font(.system(size: 14))
                            .foregroundColor(selectedIndex == i ? Color(hex: "#00FF7F") : Color.white.opacity(0.7))
                    }
                    .padding(.vertical, 10)
                    .frame(maxWidth: .infinity)
                }
            }
        }
        .padding(.horizontal)
        .background(
            LinearGradient(
                gradient: Gradient(colors: [Color(hex: "#001F3F"), Color(hex: "#001A33")]),
                startPoint: .top,
                endPoint: .bottom
            )
        )
        .overlay(
            Rectangle()
                .frame(height: 1)
                .foregroundColor(Color.white.opacity(0.2)),
            alignment: .top
        )
    }
}
