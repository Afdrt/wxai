import openai
from typing import Dict, Optional

class AIHandler:
    def __init__(self, config: dict):
        self.config = config
        self.service = config.get('service', 'openai')
        self.setup_service()
    
    def setup_service(self) -> None:
        """设置AI服务"""
        if self.service == 'openai':
            openai.api_key = self.config.get('api_key')
            api_base = self.config.get('api_base')
            if api_base:
                openai.api_base = api_base
    
    def process_message(self, message: str) -> Optional[str]:
        """处理消息并获取AI响应"""
        try:
            if self.service == 'openai':
                response = openai.ChatCompletion.create(
                    model=self.config.get('model', 'gpt-3.5-turbo'),
                    messages=[{
                        'role': 'user',
                        'content': message
                    }],
                    temperature=self.config.get('temperature', 0.7),
                    max_tokens=self.config.get('max_tokens', 1000)
                )
                return response.choices[0].message.content
            return None
        except Exception as e:
            print(f"AI处理消息失败: {str(e)}")
            return None
    
    def update_config(self, new_config: Dict) -> None:
        """更新AI配置"""
        self.config.update(new_config)
        self.setup_service()