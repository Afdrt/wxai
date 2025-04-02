import json
import os

# 加载配置文件
config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
try:
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
except Exception as e:
    print(f"加载配置文件失败: {str(e)}")
    config = {}

# UI配置
UI_CONFIG = {
    'window_title': config.get('window_title', '微信AI助手'),
    'window_size': config.get('window_size', [800, 600])
}

# 微信配置
WECHAT_CONFIG = {
    'listen_targets': config.get('listen_targets', [])
}

# AI配置
AI_CONFIG = {
    'api_key': config.get('api_key', ''),
    'service': config.get('service', 'https://api.siliconflow.cn/v1'),
    'model': config.get('model', 'deepseek-ai/DeepSeek-R1-Distill-Qwen-7B'),
    'temperature': config.get('ai_behavior', {}).get('temperature', 0.7),
    'max_tokens': config.get('ai_behavior', {}).get('max_tokens', 800),
    'system_prompt': config.get('ai_behavior', {}).get('system_prompt', 
        "你是一个友好的AI助手，请用简洁自然的方式回复用户的问题。"),
    'presence_penalty': config.get('ai_behavior', {}).get('presence_penalty', 0.9),
    'frequency_penalty': config.get('ai_behavior', {}).get('frequency_penalty', 0.0),
    'top_p': config.get('ai_behavior', {}).get('top_p', 0.0),
    'timeout': config.get('timeout', 30)
}