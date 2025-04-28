"""
初始化 Cosmos DB 数据库和容器的脚本

使用方法:
1. 确保已在 .env 文件中设置 COSMOS_ENDPOINT, COSMOS_KEY 和 COSMOS_DATABASE
2. 运行 python -m backend.scripts.init_cosmos_db
"""

import os
import sys
import json
import logging
from pathlib import Path
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from dotenv import load_dotenv

# 设置日志
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 确保脚本可以导入上层包
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(parent_dir)
sys.path.append(root_dir)

# 加载环境变量
load_dotenv(os.path.join(parent_dir, '.env'))

def create_database_if_not_exists(client, database_name):
    """创建数据库（如果不存在）"""
    try:
        database = client.create_database_if_not_exists(id=database_name)
        logger.info(f"确保数据库 {database_name} 存在")
        return database
    except exceptions.CosmosHttpResponseError as e:
        logger.error(f"创建数据库时出错: {str(e)}")
        raise

def create_container_if_not_exists(database, container_name, partition_key):
    """创建容器（如果不存在）"""
    try:
        container = database.create_container_if_not_exists(
            id=container_name,
            partition_key=PartitionKey(path=partition_key),
            offer_throughput=400  # 最小吞吐量
        )
        logger.info(f"确保容器 {container_name} 存在")
        return container
    except exceptions.CosmosHttpResponseError as e:
        logger.error(f"创建容器 {container_name} 时出错: {str(e)}")
        raise

def migrate_json_to_cosmos(container, json_file_path, transform_func=None):
    """将JSON文件中的数据迁移到Cosmos DB容器"""
    try:
        # 检查文件是否存在
        if not os.path.exists(json_file_path):
            logger.warning(f"文件 {json_file_path} 不存在，跳过迁移")
            return
        
        # 读取JSON文件
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 使用转换函数处理数据（如果提供）
        if transform_func:
            items = transform_func(data)
        else:
            items = data
        
        # 如果items不是列表，将其转换为列表
        if not isinstance(items, list):
            items = [items]
        
        # 上传到Cosmos DB
        for item in items:
            # 确保每个项目都有id
            if 'id' not in item:
                item['id'] = item.get('user_id', str(hash(json.dumps(item))))
            
            try:
                container.create_item(body=item)
                logger.info(f"成功上传项目: {item['id']}")
            except exceptions.CosmosResourceExistsError:
                logger.warning(f"项目 {item['id']} 已存在，跳过")
            except Exception as e:
                logger.error(f"上传项目 {item['id']} 时出错: {str(e)}")
        
    except Exception as e:
        logger.error(f"从 {json_file_path} 迁移数据时出错: {str(e)}")

def transform_user_profiles(data):
    """转换user_profile.json的数据格式"""
    # 如果数据是字典（如user_profile.json），将其转换为列表
    if isinstance(data, dict):
        result = []
        for user_id, profile in data.items():
            # 确保每个配置文件都有id字段
            if 'id' not in profile:
                profile['id'] = user_id
            result.append(profile)
        return result
    return data

def transform_memory_data(data):
    """转换memory.json的数据格式"""
    result = []
    
    # 处理用户交互和情绪历史
    if 'users' in data:
        for user_id, user_data in data['users'].items():
            # 处理交互
            for i, interaction in enumerate(user_data.get('interactions', [])):
                interaction_id = f"int_{i}_{user_id}"
                new_interaction = {
                    'id': interaction_id,
                    'user_id': user_id,
                    'timestamp': interaction.get('timestamp'),
                    'text': interaction.get('text'),
                    'emotion': interaction.get('emotion'),
                    'suggestion': interaction.get('suggestion'),
                    'metadata': {}
                }
                result.append(('interactions', new_interaction))
                
                # 创建嵌入记录
                embedding_id = f"emb_{i}_{user_id}"
                new_embedding = {
                    'id': embedding_id,
                    'user_id': user_id,
                    'source_type': 'interaction',
                    'source_id': interaction_id,
                    'timestamp': interaction.get('timestamp'),
                    'text': interaction.get('text'),
                    'summary': f"用户表达了{interaction.get('emotion')}情绪: {interaction.get('text')[:50]}...",
                    'memory_type': 'emotion',
                    'keywords': interaction.get('text', '').lower().split()[:10]
                }
                result.append(('memory_embeddings', new_embedding))
            
            # 处理情绪历史
            for i, emotion in enumerate(user_data.get('emotion_history', [])):
                emotion_id = f"emo_{i}_{user_id}"
                new_emotion = {
                    'id': emotion_id,
                    'user_id': user_id,
                    'timestamp': emotion.get('timestamp'),
                    'emotion': emotion.get('emotion'),
                    'confidence': emotion.get('confidence', 0.8)
                }
                result.append(('emotion_history', new_emotion))
    
    return result

def main():
    # 从环境变量获取连接信息
    cosmos_endpoint = os.getenv("COSMOS_ENDPOINT")
    cosmos_key = os.getenv("COSMOS_KEY")
    database_name = os.getenv("COSMOS_DATABASE", "emotion_agent_db")
    
    if not cosmos_endpoint or not cosmos_key:
        logger.error("环境变量 COSMOS_ENDPOINT 和 COSMOS_KEY 必须设置")
        return
    
    try:
        # 初始化 Cosmos 客户端
        client = CosmosClient(cosmos_endpoint, credential=cosmos_key)
        
        # 创建数据库
        database = create_database_if_not_exists(client, database_name)
        
        # 创建容器
        containers = {
            'user_profiles': create_container_if_not_exists(database, 'user_profiles', '/user_id'),
            'interactions': create_container_if_not_exists(database, 'interactions', '/user_id'),
            'emotion_history': create_container_if_not_exists(database, 'emotion_history', '/user_id'),
            'memory_embeddings': create_container_if_not_exists(database, 'memory_embeddings', '/user_id'),
            'conversations': create_container_if_not_exists(database, 'conversations', '/user_id')
        }
        
        # 内存文件路径
        memory_dir = os.path.join(parent_dir, 'memory')
        
        # 迁移用户配置文件
        user_profile_path = os.path.join(memory_dir, 'user_profile.json')
        migrate_json_to_cosmos(
            containers['user_profiles'], 
            user_profile_path, 
            transform_user_profiles
        )
        
        # 迁移记忆数据
        memory_path = os.path.join(memory_dir, 'memory.json')
        memory_data = transform_memory_data(json.load(open(memory_path, 'r', encoding='utf-8')))
        
        # 将转换后的记忆数据分类上传到相应的容器
        for container_name, item in memory_data:
            migrate_json_to_cosmos(containers[container_name], None, lambda x: [item])
        
        logger.info("Cosmos DB 初始化和数据迁移完成!")
        
    except Exception as e:
        logger.error(f"初始化 Cosmos DB 时出错: {str(e)}")

if __name__ == "__main__":
    main() 