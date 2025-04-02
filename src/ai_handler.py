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
            self.logger.info(f'开始处理消息: {message}')
            messages = [
                {
                    "role": "system",
                    "content": self.config.get('system_prompt', 
                        "你是一个友好的AI助手，请用简洁自然的方式回复用户的问题。")
                }
            ]
            if context:
                self.logger.debug(f'使用上下文: {context}')
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
                max_tokens=self.config.get('max_tokens', 1000)
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
    
    def update_config(self, new_config: Dict) -> None:
        """更新AI配置
        
        Args:
            new_config: 新的配置字典
        
        Raises:
            ConfigurationError: 更新配置过程中发生错误
        """
        try:
            self.config.update(new_config)
            self.service = self.config.get('service', 'openai')
            self.setup_service()
            self.logger.info('成功更新AI配置')
        except Exception as e:
            error_msg = f'更新配置失败: {str(e)}'
            self.logger.error(error_msg)
            raise ConfigurationError(error_msg)