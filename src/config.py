# AI和微信配置文件

# 微信监听配置
WECHAT_CONFIG = {
    # 指定要监听的聊天对象列表，为空则监听所有对象
    'listen_targets': ['微信支付', '文件传输助手'],
    # 是否保存图片、文件和语音消息
    'save_media': {
        'savepic': True,
        'savefile': True,
        'savevoice': True
    }
}

# AI配置
AI_CONFIG = {
    # 这里可以配置不同的AI服务，如OpenAI、Azure等
    'service': 'https://api.siliconflow.cn/v1',
    'api_key': 'sk-teubpqfpiinyfwcehgqqvrphjosxuipmebakmewxtzmebyee',  # 在实际使用时需要填入有效的API密钥
    'model': 'deepseek-ai/DeepSeek-R1-Distill-Qwen-7B',
    'temperature': 0.7,
    'max_tokens': 1000
}

# UI配置
UI_CONFIG = {
    'window_title': '微信AI助手',
    'window_size': (800, 600),
    'theme': 'light',  # light或dark
    'font_size': 12
}