#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import datetime
import collections
from collections import Counter
from typing import List, Dict, Tuple, Any, Set, Optional


class ContextStore:
    """
    管理用户交互记忆和情绪上下文的存储类。
    负责读取、写入和分析保存在JSON文件中的用户交互历史。
    """
    
    def __init__(self, memory_file: str = "memory.json"):
        """
        初始化上下文存储
        
        Args:
            memory_file: 内存文件的路径，默认为当前目录下的memory.json
        """
        self.memory_file = memory_file
        self.memory = self._load_memory()
        
    def _load_memory(self) -> Dict:
        """加载内存文件，如果不存在则返回初始结构"""
        try:
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # 返回默认结构
            return {
                "version": "2.0",
                "last_updated": self._get_timestamp(),
                "users": {}
            }
    
    def save_memory(self, output_file: Optional[str] = None) -> None:
        """
        保存内存到文件
        
        Args:
            output_file: 输出文件路径，如果为None则使用初始化时的路径
        """
        output_path = output_file or self.memory_file
        self.memory["last_updated"] = self._get_timestamp()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, indent=2, ensure_ascii=False)
    
    def _get_timestamp(self) -> str:
        """生成当前的ISO格式时间戳"""
        return datetime.datetime.now().isoformat()
    
    def get_users(self) -> List[str]:
        """
        获取所有用户ID列表
        
        Returns:
            用户ID列表
        """
        return list(self.memory.get("users", {}).keys())
    
    def add_interaction(
        self, 
        user_id: str, 
        text: str, 
        emotion: str, 
        suggestion: str,
        confidence: float = 0.0,
        metadata: Dict = None,
        timestamp: str = None
    ) -> str:
        """
        添加新的用户交互
        
        Args:
            user_id: 用户ID
            text: 用户文本
            emotion: 检测到的情绪
            suggestion: 给用户的建议
            confidence: 情绪检测的置信度
            metadata: 额外元数据
            timestamp: 时间戳，如果为None则使用当前时间
            
        Returns:
            添加交互的时间戳
        """
        # 确保用户存在
        if user_id not in self.memory.get("users", {}):
            self.memory.setdefault("users", {})[user_id] = {
                "interactions": [],
                "emotion_history": [],
                "last_active": self._get_timestamp(),
                "created_at": self._get_timestamp(),
                "stats": {
                    "total_interactions": 0,
                    "most_frequent_emotion": None,
                    "average_feedback": 0
                }
            }
        
        # 设置时间戳
        ts = timestamp or self._get_timestamp()
        
        # 创建交互记录
        interaction = {
            "timestamp": ts,
            "text": text,
            "emotion": emotion,
            "confidence": confidence,
            "suggestion": suggestion,
            "metadata": metadata or {}
        }
        
        # 创建情绪历史记录
        emotion_record = {
            "timestamp": ts,
            "emotion": emotion,
            "confidence": confidence,
            "context": text
        }
        
        # 更新用户数据
        user_data = self.memory["users"][user_id]
        user_data["interactions"].append(interaction)
        user_data["emotion_history"].append(emotion_record)
        user_data["last_active"] = ts
        
        # 更新统计信息
        user_data["stats"]["total_interactions"] += 1
        self._update_user_stats(user_id)
        
        return ts
    
    def add_feedback(
        self, 
        user_id: str, 
        interaction_timestamp: str, 
        rating: int, 
        text: str = ""
    ) -> bool:
        """
        为特定交互添加反馈
        
        Args:
            user_id: 用户ID
            interaction_timestamp: 交互的时间戳
            rating: 评分 (1-5)
            text: 反馈文本
            
        Returns:
            是否成功添加反馈
        """
        if user_id not in self.memory.get("users", {}):
            return False
        
        user_data = self.memory["users"][user_id]
        
        # 查找匹配的交互
        for interaction in user_data["interactions"]:
            if interaction["timestamp"] == interaction_timestamp:
                interaction["feedback"] = {
                    "timestamp": self._get_timestamp(),
                    "rating": rating,
                    "text": text
                }
                # 更新统计信息
                self._update_user_stats(user_id)
                return True
        
        return False
    
    def _update_user_stats(self, user_id: str) -> None:
        """更新用户的统计信息"""
        if user_id not in self.memory.get("users", {}):
            return
        
        user_data = self.memory["users"][user_id]
        interactions = user_data["interactions"]
        emotions = [interaction["emotion"] for interaction in interactions]
        
        # 最常见情绪
        if emotions:
            most_frequent = Counter(emotions).most_common(1)
            user_data["stats"]["most_frequent_emotion"] = most_frequent[0][0] if most_frequent else None
        
        # 平均反馈分数
        feedback_ratings = [
            interaction["feedback"]["rating"] 
            for interaction in interactions 
            if "feedback" in interaction and interaction["feedback"] is not None
        ]
        
        if feedback_ratings:
            user_data["stats"]["average_feedback"] = sum(feedback_ratings) / len(feedback_ratings)
        else:
            user_data["stats"]["average_feedback"] = 0
    
    def get_recent_emotions(self, user_id: str, limit: int = 5) -> List[Dict]:
        """
        获取用户最近的情绪记录
        
        Args:
            user_id: 用户ID
            limit: 要返回的记录数
            
        Returns:
            最近的情绪记录列表
        """
        if user_id not in self.memory.get("users", {}):
            return []
        
        user_data = self.memory["users"][user_id]
        emotions = user_data.get("emotion_history", [])
        
        # 按时间戳倒序排序并截取指定数量
        sorted_emotions = sorted(emotions, key=lambda x: x["timestamp"], reverse=True)
        return sorted_emotions[:limit]
    
    def get_emotion_trend(self, user_id: str, days: int = 7) -> Dict[str, List[str]]:
        """
        获取用户在指定天数内的情绪趋势
        
        Args:
            user_id: 用户ID
            days: 要回溯的天数
            
        Returns:
            每天的情绪列表，以日期为键
        """
        if user_id not in self.memory.get("users", {}):
            return {}
        
        result = {}
        today = datetime.datetime.now().date()
        
        # 初始化结果字典，包含过去指定天数的日期
        for i in range(days):
            date = (today - datetime.timedelta(days=i)).isoformat()
            result[date] = []
        
        # 获取情绪历史
        user_data = self.memory["users"][user_id]
        emotions = user_data.get("emotion_history", [])
        
        for emotion in emotions:
            timestamp = emotion["timestamp"]
            try:
                date = datetime.datetime.fromisoformat(timestamp).date().isoformat()
                # 只添加在请求的日期范围内的情绪
                if date in result:
                    result[date].append(emotion["emotion"])
            except ValueError:
                # 无效时间戳，跳过
                continue
        
        return result
    
    def get_frequent_contexts(self, user_id: str, limit: int = 10) -> List[Tuple[str, int]]:
        """
        获取用户交互中最常出现的上下文单词
        
        Args:
            user_id: 用户ID
            limit: 要返回的最常见单词数量
            
        Returns:
            (单词, 出现次数) 元组列表
        """
        if user_id not in self.memory.get("users", {}):
            return []
        
        # 从用户交互中提取所有文本
        user_data = self.memory["users"][user_id]
        texts = [interaction["text"] for interaction in user_data.get("interactions", [])]
        
        # 将文本分割成单词，并过滤掉常见的停用词
        all_words = []
        stop_words = {"i", "me", "my", "myself", "we", "our", "ours", "ourselves", 
                      "you", "your", "yours", "yourself", "yourselves", 
                      "he", "him", "his", "himself", "she", "her", "hers", 
                      "herself", "it", "its", "itself", "they", "them", 
                      "their", "theirs", "themselves", "what", "which", 
                      "who", "whom", "this", "that", "these", "those", 
                      "am", "is", "are", "was", "were", "be", "been", "being", 
                      "have", "has", "had", "having", "do", "does", "did", 
                      "doing", "a", "an", "the", "and", "but", "if", "or", 
                      "because", "as", "until", "while", "of", "at", "by", 
                      "for", "with", "about", "against", "between", "into", 
                      "through", "during", "before", "after", "above", "below", 
                      "to", "from", "up", "down", "in", "out", "on", "off", 
                      "over", "under", "again", "further", "then", "once"}
        
        for text in texts:
            words = text.lower().split()
            filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
            all_words.extend(filtered_words)
        
        # 计算单词频率并返回最常见的单词
        word_counts = Counter(all_words)
        return word_counts.most_common(limit)
    
    def get_active_days(self, user_id: str) -> Set[str]:
        """
        获取用户活跃的日期集合
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户活跃日期的集合
        """
        if user_id not in self.memory.get("users", {}):
            return set()
        
        user_data = self.memory["users"][user_id]
        timestamps = [interaction["timestamp"] for interaction in user_data.get("interactions", [])]
        
        active_days = set()
        for timestamp in timestamps:
            try:
                date = datetime.datetime.fromisoformat(timestamp).date().isoformat()
                active_days.add(date)
            except ValueError:
                # 无效时间戳，跳过
                continue
        
        return active_days
    
    def get_emotion_distribution(self, user_id: str) -> Dict[str, int]:
        """
        获取用户情绪分布
        
        Args:
            user_id: 用户ID
            
        Returns:
            情绪及其出现次数的字典
        """
        if user_id not in self.memory.get("users", {}):
            return {}
        
        user_data = self.memory["users"][user_id]
        emotions = [interaction["emotion"] for interaction in user_data.get("interactions", [])]
        
        return dict(Counter(emotions))
    
    def get_relevant_interactions(self, user_id: str, query: str, limit: int = 3) -> List[Dict]:
        """
        通过简单关键词匹配获取与查询相关的交互
        
        Args:
            user_id: 用户ID
            query: 搜索查询
            limit: 要返回的最大结果数
            
        Returns:
            相关交互列表
        """
        if user_id not in self.memory.get("users", {}):
            return []
        
        user_data = self.memory["users"][user_id]
        interactions = user_data.get("interactions", [])
        
        # 简单关键词匹配
        query_terms = query.lower().split()
        scored_interactions = []
        
        for interaction in interactions:
            text = interaction["text"].lower()
            score = sum(1 for term in query_terms if term in text)
            if score > 0:
                scored_interactions.append((score, interaction))
        
        # 按相关性得分排序
        scored_interactions.sort(reverse=True)
        
        # 返回前N个结果
        return [interaction for _, interaction in scored_interactions[:limit]] 