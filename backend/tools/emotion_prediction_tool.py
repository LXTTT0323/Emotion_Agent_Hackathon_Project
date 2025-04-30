import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
import os
from typing import Dict, Any
from pathlib import Path

# 全局变量
_model = None
_emotion_labels = {
    0: "baseline",
    1: "stress",
    2: "amusement"
}
_question_templates = {
    "baseline": [
        "看起来你现在的心情比较平静呢，是这样吗？",
        "感觉你现在的状态很稳定，想聊聊今天的感受吗？",
        "你似乎处于一个比较放松的状态，要分享一下吗？"
    ],
    "stress": [
        "我注意到你可能有些紧张或压力，愿意和我说说吗？",
        "最近是不是遇到了什么困扰的事情？",
        "感觉你的压力水平有点高，需要聊一聊吗？"
    ],
    "amusement": [
        "看起来你的心情不错呢！发生了什么开心的事吗？",
        "感觉你现在很愉快，要分享一下快乐的源泉吗？",
        "你似乎心情很好，是有什么好事要分享吗？"
    ]
}

def _load_model():
    """加载LSTM模型"""
    global _model
    if _model is None:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        model_path = os.path.join(project_root, "model", "lstm_emotion_model.h5")
        _model = load_model(model_path)
    return _model

def _preprocess_health_data(health_data: Dict) -> np.ndarray:
    """预处理健康数据，转换为模型输入格式"""
    # 将健康数据转换为DataFrame
    df = pd.DataFrame([{
        'hrv_sdnn': health_data['hrv']['sdnn'],
        'heart_rate': health_data['heart_rate']['avg'],
        'sleep_time': health_data['sleep']['total_minutes'] / 60  # 转换为小时
    }])
    
    # 创建特征
    df['HRV_SDNN'] = df['hrv_sdnn']
    df['HRV_SDNN_lag1'] = df['HRV_SDNN'].shift(1)
    df['HRV_SDNN_lag2'] = df['HRV_SDNN'].shift(2)
    
    # 填充缺失值
    df = df.fillna(method='ffill').fillna(0)
    
    # 选择特征列
    features = ['HRV_SDNN', 'HRV_SDNN_lag1', 'HRV_SDNN_lag2']
    X = df[features].values
    
    # reshape为LSTM输入格式 (samples, time_steps, features)
    X = X.reshape((1, 1, len(features)))
    
    return X

def _generate_question(emotion: str) -> str:
    """根据预测的情绪生成问题"""
    templates = _question_templates.get(emotion, _question_templates["baseline"])
    return np.random.choice(templates)

async def predict_emotion_and_generate_question(health_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tool to predict emotion from health data and generate appropriate questions.
    
    This tool:
    1. Preprocesses the health data (HRV, heart rate, sleep)
    2. Uses LSTM model to predict emotional state
    3. Generates an appropriate question based on the predicted emotion
    
    Input: Dict with health metrics (heart rate, HRV, sleep, etc.)
    Output: Dict with predicted emotion, probabilities and generated question
    """
    try:
        # 加载模型
        model = _load_model()
        
        # 预处理数据
        X = _preprocess_health_data(health_data)
        
        # 模型预测
        predictions = model.predict(X)
        emotion_probs = {_emotion_labels[i]: float(prob) 
                        for i, prob in enumerate(predictions[0])}
        
        # 获取最可能的情绪
        predicted_emotion = _emotion_labels[np.argmax(predictions[0])]
        
        # 生成问题
        question = _generate_question(predicted_emotion)
        
        return {
            "predicted_emotion": predicted_emotion,
            "emotion_probabilities": emotion_probs,
            "generated_question": question
        }
    except Exception as e:
        print(f"Error predicting emotion: {str(e)}")
        return {
            "error": f"Failed to predict emotion: {str(e)}"
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