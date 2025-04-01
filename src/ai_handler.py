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
    
    def setup_service(self) -> None:
        """设置AI服务配置"""
        try:
            # 配置API密钥
            api_key = self.config.get('api_key')
            if not api_key:
                raise ConfigurationError('API密钥未配置')
            openai.api_key = api_key
            
            # 配置API服务地址
            service_url = self.config.get('service')
            if service_url:
                openai.api_base = service_url
                self.logger.info(f'使用自定义服务地址: {service_url}')
            
            self.logger.info('成功配置AI服务')
        except Exception as e:
            self.logger.error(f'设置AI服务失败: {str(e)}')
            raise ConfigurationError(f'设置AI服务失败: {str(e)}')
    
    def process_message(self, message: str, context: List[Dict] = None) -> Optional[str]:
        """处理消息并获取AI响应
        
        Args:
            message: 用户输入的消息
            context: 可选的上下文消息列表，每个消息是包含role和content的字典
        
        Returns:
            AI的响应文本，如果处理失败则返回None
        
        Raises:
            ProcessingError: 消息处理过程中发生错误
        """
        try:
            messages = []
            if context:
                messages.extend(context)
            messages.append({
                'role': 'user',
                'content': message
            })
            
            response = openai.ChatCompletion.create(
                model=self.config.get('model'),
                messages=messages,
                temperature=self.config.get('temperature', 0.7),
                max_tokens=self.config.get('max_tokens', 1000)
            )
            
            reply = response.choices[0].message.content
            self.logger.debug(f'AI响应: {reply}')
            return reply
        except Exception as e:
            error_msg = f'处理消息失败: {str(e)}'
            self.logger.error(error_msg)
            raise ProcessingError(error_msg)
    
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