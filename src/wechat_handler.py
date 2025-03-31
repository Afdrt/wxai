from wxauto import *
import time
import datetime
from typing import Dict, List, Any, Optional

class WeChatHandler:
    def __init__(self, config: dict):
        self.config = config
        self.wx = WeChat()
        self.listen_targets = config.get('listen_targets', [])
        self.save_media = config.get('save_media', {})
        self.last_msg_ids = {}
        self.start_time = time.time()
        
    def initialize(self) -> str:
        """初始化微信客户端并返回当前登录账号"""
        return self.wx.nickname
    
    def setup_listeners(self) -> List[str]:
        """设置消息监听"""
        success_targets = []
        if self.listen_targets:
            for target in self.listen_targets:
                try:
                    self.wx.AddListenChat(
                        target,
                        savepic=self.save_media.get('savepic', True),
                        savefile=self.save_media.get('savefile', True),
                        savevoice=self.save_media.get('savevoice', True)
                    )
                    success_targets.append(target)
                except Exception as e:
                    print(f"添加监听对象 {target} 失败: {str(e)}")
        return success_targets
    
    def process_message(self, msg: Any) -> Dict[str, str]:
        """处理单条消息，返回格式化的消息信息"""
        try:
            if hasattr(msg, '__class__') and msg.__class__.__name__ == 'SysMessage':
                return {
                    'type': '系统消息',
                    'content': str(msg),
                    'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'id': '系统消息ID'
                }
            else:
                return {
                    'type': msg[0] if isinstance(msg, (list, tuple)) and len(msg) > 0 else '未知类型',
                    'content': msg[1] if isinstance(msg, (list, tuple)) and len(msg) > 1 else str(msg),
                    'time': msg[2] if isinstance(msg, (list, tuple)) and len(msg) > 2 else datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'id': msg[-1] if isinstance(msg, (list, tuple)) and len(msg) > 3 else '未知ID'
                }
        except Exception as e:
            return {
                'type': '处理错误',
                'content': f"消息处理错误: {str(e)}, 原始消息: {str(msg)}",
                'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'id': '错误ID'
            }
    
    def get_new_messages(self) -> Dict[str, List[Dict[str, str]]]:
        """获取新消息"""
        messages_by_sender = {}
        
        if self.listen_targets:
            for target in self.listen_targets:
                new_messages = self.wx.GetListenMessage(target)
                if new_messages:
                    messages_by_sender[target] = [
                        self.process_message(msg) for msg in new_messages
                    ]
        else:
            if self.wx.CheckNewMessage():
                new_msg = self.wx.GetNextNewMessage(
                    savepic=self.save_media.get('savepic', True),
                    savefile=self.save_media.get('savefile', True),
                    savevoice=self.save_media.get('savevoice', True)
                )
                
                if new_msg:
                    for chat_name, messages in new_msg.items():
                        processed_messages = []
                        for msg in messages:
                            if isinstance(msg, (list, tuple)) and len(msg) > 3:
                                msg_id = msg[-1]
                                if chat_name not in self.last_msg_ids or msg_id not in self.last_msg_ids[chat_name]:
                                    processed_messages.append(self.process_message(msg))
                                    if chat_name not in self.last_msg_ids:
                                        self.last_msg_ids[chat_name] = []
                                    self.last_msg_ids[chat_name].append(msg_id)
                            else:
                                processed_messages.append(self.process_message(msg))
                        
                        if processed_messages:
                            messages_by_sender[chat_name] = processed_messages
        
        return messages_by_sender
    
    def send_message(self, content: str, target: str) -> bool:
        """发送消息到指定目标"""
        try:
            self.wx.SendMsg(content, who=target)
            return True
        except Exception as e:
            print(f"向 {target} 发送消息失败: {str(e)}")
            return False
    
    def cleanup(self) -> None:
        """清理监听对象"""
        if self.listen_targets:
            for target in self.listen_targets:
                try:
                    self.wx.RemoveListenChat(target)
                except Exception as e:
                    print(f"移除监听对象 {target} 失败: {str(e)}")
    