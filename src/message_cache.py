from datetime import datetime
from typing import Optional, Dict, List

class MessageCache:
    def __init__(self, response_delay: int = 3):
        self.user_messages: Dict[str, List[Dict]] = {}
        self.last_message_time: Dict[str, datetime] = {}
        self.response_delay = response_delay  # 延迟响应时间（秒）
    
    def add_message(self, sender: str, content: str) -> None:
        """添加新消息到缓存，并重置计时"""
        if sender not in self.user_messages:
            self.user_messages[sender] = []
            
        self.user_messages[sender].append({
            'content': content,
            'time': datetime.now()
        })
        # 更新最后消息时间
        self.last_message_time[sender] = datetime.now()
    
    def get_combined_messages(self, sender: str) -> Optional[str]:
        """获取并清空用户的缓存消息"""
        if sender not in self.user_messages or not self.user_messages[sender]:
            return None
            
        current_time = datetime.now()
        if sender in self.last_message_time:
            time_diff = (current_time - self.last_message_time[sender]).total_seconds()
            # 只有当距离最后一条消息超过3秒时才返回
            if time_diff >= self.response_delay:
                combined_message = "\n".join([f"用户: {msg['content']}" for msg in self.user_messages[sender]])
                self.user_messages[sender] = []
                return combined_message
        return None