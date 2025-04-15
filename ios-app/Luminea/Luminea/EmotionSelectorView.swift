//
//  EmotionSelectorView.swift
//  Luminea
//
//  Created by thea chen on 2025/4/13.
//

import SwiftUICore
import SwiftUI

// 弹出式情绪选择器浮层视图
struct EmotionSelectorView: View {
    @Binding var currentEmotion: EmotionType
    @Binding var isPresented: Bool

    let columns = [GridItem(.flexible()), GridItem(.flexible()), GridItem(.flexible())]

    var body: some View {
        VStack {
            Spacer()
            VStack(spacing: 16) {
                Text("选择你的情绪")
                    .font(.headline)
                    .foregroundColor(.white)

                LazyVGrid(columns: columns, spacing: 12) {
                    ForEach(EmotionType.allCases, id: \.self) { emotion in
                        Button(action: {
                            withAnimation(.easeInOut(duration: 0.3)) {
                                currentEmotion = emotion
                                isPresented = false
                            }
                        }) {
                            VStack(spacing: 4) {
                                Text(emotion.rawValue)
                                    .font(.system(size: 28))
                                Text(emotion.name)
                                    .font(.footnote)
                                    .foregroundColor(.white.opacity(0.8))
                            }
                            .frame(maxWidth: .infinity)
                            .padding(8)
                            .background(emotion.color.opacity(0.2))
                            .cornerRadius(12)
                        }
                    }
                }
            }
            .padding()
            .background(.ultraThinMaterial)
            .cornerRadius(20)
            .padding(.horizontal)
            .padding(.bottom, 40)
        }
        .transition(.move(edge: .bottom).combined(with: .opacity))
    }
}
