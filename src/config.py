import json
import os

# 获取当前文件所在目录的父目录（项目根目录）
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 读取config.json文件
def load_config():
    config_path = os.path.join(ROOT_DIR, 'config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f'警告: 配置文件 {config_path} 不存在，将使用默认配置')
        return {}
    except json.JSONDecodeError:
        print(f'警告: 配置文件 {config_path} 格式错误，将使用默认配置')
        return {}
    except Exception as e:
        print(f'警告: 读取配置文件时发生错误: {str(e)}，将使用默认配置')
        return {}

# 加载配置
config = load_config()

# 微信配置
WECHAT_CONFIG = {
    'listen_targets': config.get('listen_targets', []),
    'save_media': config.get('save_media', {
        'savepic': True,
        'savefile': True,
        'savevoice': True
    })
}

# AI配置
AI_CONFIG = {
    'api_key': config.get('api_key', ''),
    'service': config.get('service', 'https://api.siliconflow.cn/v1'),
    'model': config.get('model', 'deepseek-ai/DeepSeek-R1-Distill-Qwen-7B'),
    'temperature': config.get('temperature', 0.7),
    'max_tokens': config.get('max_tokens', 1000),
    'timeout': config.get('timeout', 30)
}

# UI配置
UI_CONFIG = {
    'window_title': config.get('window_title', '微信AI助手'),
    'window_size': config.get('window_size', (800, 600))
}

# 验证必要的配置项
if not AI_CONFIG['api_key']:
    print('警告: API密钥未配置，请在config.json中设置api_key')

if not AI_CONFIG['service']:
    print('警告: AI服务地址未配置，将使用默认服务地址')