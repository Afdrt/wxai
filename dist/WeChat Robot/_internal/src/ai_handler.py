import logging
import openai
from typing import Dict, Optional, List

class AIServiceError(Exception):
    """AI服务异常基类"""
    pass

class ConfigurationError(AIServiceError):
    """配置错误异常"""
    pass

class ProcessingError(AIServiceError):
    """消息处理异常"""
    pass

class AIHandler:
    def __init__(self, config: dict):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.service = 'openai'  # 默认使用openai服务
        self.setup_service()
    
    def process_message(self, message: str, context: List[Dict] = None) -> Optional[str]:
        """处理消息并获取AI响应"""
        try:
            self.logger.info(f'开始处理消息: {message[:100]}{"..." if len(message) > 100 else ""}')
            messages = [
                {
                    "role": "system",
                    "content": self.config.get('system_prompt', 
                        "你是一个友好的AI助手，请用简洁自然的方式回复用户的问题。")
                }
            ]
            if context:
                self.logger.debug(f'使用上下文: {len(context)} 条消息')
                messages.extend(context)
            messages.append({
                'role': 'user',
                'content': message
            })
            
            self.logger.info(f'使用模型 {self.config.get("model")} 发送请求')
            client = openai.OpenAI(
                api_key=self.config['api_key'],
                base_url=self.config.get('service')
            )
            
            response = client.chat.completions.create(
                model=self.config.get('model'),
                messages=messages,
                temperature=self.config.get('temperature', 0.7),
                max_tokens=self.config.get('max_tokens', 800),
                presence_penalty=self.config.get('presence_penalty', 0.9),
                frequency_penalty=self.config.get('frequency_penalty', 0.0),
                top_p=self.config.get('top_p', 0.0)
            )
            
            reply = response.choices[0].message.content
            self.logger.info(f'收到AI响应: {reply[:100]}{"..." if len(reply) > 100 else ""}')
            return reply
        except Exception as e:
            error_msg = f'处理消息失败: {str(e)}'
            self.logger.error(error_msg, exc_info=True)  # 添加异常堆栈信息
            raise ProcessingError(error_msg)
    
    def setup_service(self) -> None:
        """设置AI服务配置"""
        try:
            self.logger.info('开始配置AI服务...')
            # 配置API密钥
            api_key = self.config.get('api_key')
            if not api_key:
                self.logger.error('API密钥未配置')
                raise ConfigurationError('API密钥未配置')
            openai.api_key = api_key
            self.logger.debug('API密钥配置成功')
            
            # 配置API服务地址
            service_url = self.config.get('service')
            if service_url:
                openai.api_base = service_url
                self.logger.info(f'使用自定义服务地址: {service_url}')
            
            self.logger.info('AI服务配置完成')
        except Exception as e:
            error_msg = f'设置AI服务失败: {str(e)}'
            self.logger.error(error_msg, exc_info=True)  # 添加异常堆栈信息
            raise ConfigurationError(error_msg)
    
    def update_config(self, config: dict) -> None:
        """更新AI配置"""
        self.logger.info("更新AI配置")
        self.api_key = config.get('api_key', '')
        self.service = config.get('service', '')
        self.model = config.get('model', 'gpt-3.5-turbo')
        self.system_prompt = config.get('system_prompt', '')
        self.temperature = config.get('temperature', 0.7)
        self.max_tokens = config.get('max_tokens', 2000)
        self.presence_penalty = config.get('presence_penalty', 0)
        self.frequency_penalty = config.get('frequency_penalty', 0)
        self.top_p = config.get('top_p', 1.0)
        
        # 重新初始化客户端
        # 使用与__init__方法中相同的初始化逻辑，而不是调用不存在的_init_client方法
        try:
            self.logger.info("开始配置AI服务...")
            
            # 设置API密钥
            openai.api_key = self.api_key
            
            # 如果提供了自定义服务地址，则设置
            if self.service:
                self.logger.info(f"使用自定义服务地址: {self.service}")
                openai.api_base = self.service
            
            self.logger.info("AI服务配置完成")
        except Exception as e:
            self.logger.error(f"AI服务配置失败: {str(e)}")
            raise ConfigurationError(f"AI服务配置失败: {str(e)}")