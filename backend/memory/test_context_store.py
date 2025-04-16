#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import datetime
from context_store import ContextStore


def print_separator(title):
    """打印带标题的分隔线"""
    print("\n" + "=" * 50)
    print(f"    {title}")
    print("=" * 50)


def main():
    print_separator("初始化上下文存储")
    memory_file = "memory.json"
    
    # 如果已经存在初始文件，先读取它
    if os.path.exists(memory_file):
        with open(memory_file, 'r', encoding='utf-8') as f:
            print(f"已发现现有记忆文件: {memory_file}")
    else:
        print(f"未找到记忆文件，将创建新的: {memory_file}")
    
    # 初始化上下文存储
    context_store = ContextStore(memory_file)
    
    # 展示当前用户列表
    print_separator("用户列表")
    users = context_store.get_users()
    print(f"找到 {len(users)} 个用户:")
    for user in users:
        print(f"- {user}")
    
    # 如果没有用户，添加测试用户
    test_user_id = "test_user_123"
    if not users:
        print(f"\n添加测试用户: {test_user_id}")
        # 添加一些测试交互
        context_store.add_interaction(
            user_id=test_user_id,
            text="我今天感觉很开心，工作进展顺利！",
            emotion="happy",
            confidence=0.92,
            suggestion="很高兴听到你今天心情不错，继续保持！",
            metadata={"time_of_day": "morning", "location": "home"}
        )
        
        context_store.add_interaction(
            user_id=test_user_id,
            text="我对即将到来的会议演讲有点紧张",
            emotion="anxious",
            confidence=0.78,
            suggestion="深呼吸，好好准备，你会做得很好的！",
            metadata={"time_of_day": "afternoon", "location": "office"}
        )
        
        context_store.add_interaction(
            user_id=test_user_id,
            text="我的演讲准备得怎么样？",
            emotion="neutral",
            confidence=0.65,
            suggestion="根据你的准备情况，可以考虑进行一次预演增强信心",
            metadata={"time_of_day": "evening", "location": "home"}
        )
        
        context_store.add_interaction(
            user_id=test_user_id,
            text="我的演讲进行得很成功，观众反应很好！",
            emotion="excited",
            confidence=0.89,
            suggestion="恭喜你！这是一个值得庆祝的成就！",
            metadata={"time_of_day": "afternoon", "location": "office"}
        )
        
        context_store.add_interaction(
            user_id=test_user_id,
            text="今天我很疲惫，工作太多了",
            emotion="tired",
            confidence=0.85,
            suggestion="建议你今晚好好休息，明天再继续处理工作",
            metadata={"time_of_day": "evening", "location": "home"}
        )
        
        # 添加多天的测试数据
        for i in range(1, 8):
            past_date = datetime.datetime.now() - datetime.timedelta(days=i)
            timestamp = past_date.isoformat()
            emotion = ["happy", "sad", "anxious", "excited", "tired"][i % 5]
            
            context_store.add_interaction(
                user_id=test_user_id,
                text=f"这是{i}天前的一条记录",
                emotion=emotion,
                confidence=0.8,
                suggestion=f"这是对{emotion}情绪的建议",
                metadata={"day": i},
                timestamp=timestamp
            )
        
        # 添加反馈
        latest_interaction = context_store.get_recent_emotions(test_user_id, limit=1)[0]
        context_store.add_feedback(
            user_id=test_user_id,
            interaction_timestamp=latest_interaction["timestamp"],
            rating=5,
            text="这个建议对我非常有帮助！"
        )
        
        print("已添加测试数据")
        users = context_store.get_users()
    
    # 选择一个用户进行分析
    selected_user = users[0] if users else test_user_id
    print(f"\n选择用户: {selected_user} 进行分析")
    
    # 显示用户的最近情绪
    print_separator("最近情绪")
    recent_emotions = context_store.get_recent_emotions(selected_user)
    for emotion in recent_emotions:
        print(f"时间: {emotion['timestamp']}")
        print(f"情绪: {emotion['emotion']} (置信度: {emotion['confidence']:.2f})")
        print(f"上下文: {emotion['context'][:50]}..." if len(emotion['context']) > 50 else emotion['context'])
        print()
    
    # 显示情绪趋势
    print_separator("过去7天情绪趋势")
    emotion_trend = context_store.get_emotion_trend(selected_user)
    for date, emotions in emotion_trend.items():
        if emotions:
            print(f"{date}: {', '.join(emotions)}")
        else:
            print(f"{date}: 无记录")
    
    # 显示最常用的上下文
    print_separator("最常用上下文")
    frequent_contexts = context_store.get_frequent_contexts(selected_user)
    if frequent_contexts:
        for context, count in frequent_contexts:
            print(f"{context}: {count}次")
    else:
        print("没有找到频繁上下文")
    
    # 显示活跃天数
    print_separator("用户活跃日")
    active_days = context_store.get_active_days(selected_user)
    print(f"用户在 {len(active_days)} 天内有活动:")
    for day in sorted(active_days):
        print(f"- {day}")
    
    # 显示情绪分布
    print_separator("情绪分布")
    emotion_distribution = context_store.get_emotion_distribution(selected_user)
    for emotion, count in emotion_distribution.items():
        print(f"{emotion}: {count}次")
    
    # 相关交互查询
    print_separator("相关交互查询")
    query = "演讲"
    relevant_interactions = context_store.get_relevant_interactions(selected_user, query)
    print(f"与'{query}'相关的交互:")
    for interaction in relevant_interactions:
        print(f"时间: {interaction['timestamp']}")
        print(f"文本: {interaction['text']}")
        print(f"情绪: {interaction['emotion']}")
        print()
    
    # 添加新交互
    print_separator("添加新交互")
    new_text = "我即将参加一个重要的演讲比赛，需要做好准备"
    timestamp = context_store.add_interaction(
        user_id=selected_user,
        text=new_text,
        emotion="determined",
        confidence=0.87,
        suggestion="提前准备并进行多次练习会增强你的信心和表现",
        metadata={"importance": "high", "type": "preparation"}
    )
    print(f"已添加新交互，时间戳: {timestamp}")
    
    # 为最新交互添加反馈
    print_separator("添加反馈")
    feedback_added = context_store.add_feedback(
        user_id=selected_user,
        interaction_timestamp=timestamp,
        rating=4,
        text="这个建议很有帮助，但我还需要更多具体的演讲技巧"
    )
    print(f"反馈添加{'成功' if feedback_added else '失败'}")
    
    # 保存更新后的记忆
    print_separator("保存更新后的记忆")
    updated_file = "memory_updated.json"
    context_store.save_memory(updated_file)
    print(f"记忆已保存到: {updated_file}")
    
    # 显示文件大小
    file_size = os.path.getsize(updated_file)
    print(f"文件大小: {file_size / 1024:.2f} KB")
    
    print("\n演示完成！")


if __name__ == "__main__":
    main() 