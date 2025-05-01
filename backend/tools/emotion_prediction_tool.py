import numpy as np
import pandas as pd
import os
import random
from typing import Dict, Any
from pathlib import Path

# 全局变量
_emotion_labels = {
    0: "baseline",
    1: "stress",
    2: "amusement"
}
_question_templates = {
    "baseline": [
        "我看到你的心率和心率变异性都很平稳...不过，最近是不是有什么事在困扰你？"
    ],
    "stress": [
        "你的心率数据告诉我，最近是不是压力有点大？要不要和我说说看..."
    ],
    "amusement": [
        "看到你的身体状态这么好，我也跟着开心起来了...最近是遇到什么好事了吗？"
    ]
}

# CSV数据源
_csv_data = None

def _load_csv_data():
    """加载CSV数据作为情绪预测的数据源"""
    global _csv_data
    if _csv_data is None:
        try:
            # 尝试加载上传的CSV文件
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            csv_path = os.path.join(project_root, "model", "HeartRateVariabilitySDNN.csv")
            
            if os.path.exists(csv_path):
                _csv_data = pd.read_csv(csv_path)
                print(f"成功加载CSV数据: {csv_path}")
                
                # 确保数据包含必要的列
                required_columns = ['hrv_sdnn', 'heart_rate']
                if not all(col in _csv_data.columns for col in required_columns):
                    print("CSV文件缺少必要的列，将使用模拟数据")
                    _csv_data = _create_mock_data()
            else:
                print(f"CSV文件不存在: {csv_path}，将使用模拟数据")
                _csv_data = _create_mock_data()
        except Exception as e:
            print(f"加载CSV数据时出错: {str(e)}，将使用模拟数据")
            _csv_data = _create_mock_data()
    
    return _csv_data

def _create_mock_data():
    """创建模拟数据"""
    return pd.DataFrame({
        'timestamp': pd.date_range(start='2023-01-01', periods=100, freq='H'),
        'hrv_sdnn': np.random.normal(50, 10, 100),
        'heart_rate': np.random.normal(75, 8, 100),
        'emotion': np.random.choice(['baseline', 'stress', 'amusement'], 100)
    })

def _predict_from_csv(health_data: Dict) -> Dict:
    """基于CSV数据预测情绪"""
    # 加载CSV数据
    df = _load_csv_data()
    
    # 获取健康数据
    hrv_sdnn = health_data['hrv']['sdnn']
    heart_rate = health_data['heart_rate']['avg']
    
    # 简单方法：找到最接近的数据点
    if 'hrv_sdnn' in df.columns and 'heart_rate' in df.columns:
        # 计算欧几里得距离
        df['distance'] = np.sqrt(
            ((df['hrv_sdnn'] - hrv_sdnn) / 50) ** 2 + 
            ((df['heart_rate'] - heart_rate) / 20) ** 2  # 归一化距离
        )
        
        # 获取最近的5个点
        nearest = df.nsmallest(5, 'distance')
        
        if 'emotion' in nearest.columns:
            # 使用最常见的情绪，考虑距离权重
            weights = 1 / (nearest['distance'] + 0.1)  # 避免除以0
            emotion_weights = {}
            for idx, row in nearest.iterrows():
                emotion = row['emotion']
                weight = weights[idx]
                emotion_weights[emotion] = emotion_weights.get(emotion, 0) + weight
            
            predicted_emotion = max(emotion_weights.items(), key=lambda x: x[1])[0]
        else:
            # 使用规则预测
            predicted_emotion = _predict_by_rule(hrv_sdnn, heart_rate)
    else:
        # 使用规则预测
        predicted_emotion = _predict_by_rule(hrv_sdnn, heart_rate)
    
    # 生成概率分布
    if predicted_emotion == "baseline":
        probs = [0.7, 0.2, 0.1]
    elif predicted_emotion == "stress":
        probs = [0.1, 0.8, 0.1]
    else:  # amusement
        probs = [0.1, 0.1, 0.8]
    
    # 添加随机性
    probs = [p + random.uniform(-0.1, 0.1) for p in probs]
    probs = [max(0.05, p) for p in probs]  # 确保概率不小于0.05
    total = sum(probs)
    probs = [p/total for p in probs]  # 归一化
    
    # 创建概率字典
    emotion_probs = {_emotion_labels[i]: float(prob) for i, prob in enumerate(probs)}
    
    return {
        "predicted_emotion": predicted_emotion,
        "emotion_probabilities": emotion_probs
    }

def _predict_by_rule(hrv_sdnn: float, heart_rate: float) -> str:
    """使用简单规则预测情绪"""
    # 更细致的规则
    if hrv_sdnn > 60:
        if heart_rate < 80:
            return "amusement"  # 高HRV，低心率 -> 愉悦
        else:
            return "baseline"   # 高HRV，高心率 -> 中性
    elif hrv_sdnn < 40:
        if heart_rate > 90:
            return "stress"     # 低HRV，高心率 -> 压力
        else:
            return "baseline"   # 低HRV，低心率 -> 中性
    else:
        if heart_rate > 95:
            return "stress"     # 中等HRV，很高心率 -> 压力
        elif heart_rate < 70:
            return "amusement"  # 中等HRV，很低心率 -> 愉悦
        else:
            return "baseline"   # 其他情况 -> 中性

def _generate_question(emotion: str) -> str:
    """根据预测的情绪生成问题"""
    templates = _question_templates.get(emotion, _question_templates["baseline"])
    return np.random.choice(templates)

async def predict_emotion_and_generate_question(health_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tool to predict emotion from health data and generate appropriate questions.
    
    This tool:
    1. Uses CSV data or rules to predict emotional state
    2. Generates an appropriate question based on the predicted emotion
    
    Input: Dict with health metrics (heart rate, HRV, sleep, etc.)
    Output: Dict with predicted emotion, probabilities and generated question
    """
    try:
        # 从CSV预测情绪
        prediction_result = _predict_from_csv(health_data)
        
        # 生成问题
        question = _generate_question(prediction_result["predicted_emotion"])
        prediction_result["generated_question"] = question
        
        return prediction_result
    except Exception as e:
        print(f"Error predicting emotion: {str(e)}")
        return {
            "error": f"Failed to predict emotion: {str(e)}",
            "predicted_emotion": "baseline",
            "emotion_probabilities": {
                "baseline": 0.7,
                "stress": 0.2,
                "amusement": 0.1
            },
            "generated_question": _generate_question("baseline")
        }

# 使用示例
if __name__ == "__main__":
    import asyncio
    
    # 示例健康数据，与fetch_health_data.py保持一致
    mock_health_data = {
        "heart_rate": {"avg": 75, "min": 62, "max": 110},
        "hrv": {"rmssd": 45.2, "sdnn": 52.8},
        "sleep": {"deep_sleep_minutes": 90, "total_minutes": 420},
        "steps": 8500,
        "menstrual_cycle": {"phase": "follicular", "day": 8},
        "timestamp": "2023-04-12T08:30:00Z"
    }
    
    # 运行异步函数
    result = asyncio.run(predict_emotion_and_generate_question(mock_health_data))
    print(result) 