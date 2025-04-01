from wxauto import WeChat
import datetime
import time
from typing import Dict, List, Optional

class WeChatHandler:
    def __init__(self, config: dict):
        self.wx = WeChat()
        self.listen_targets = config.get('listen_targets', [])
        self.start_time = time.time()
        self.ui = None
    
    def set_ui(self, ui):
        """设置UI引用"""
        self.ui = ui
    
    def initialize(self) -> str:
        """初始化微信客户端并返回当前登录账号"""
        try:
            return self.wx.nickname  # 使用 nickname 属性获取当前登录账号名称
        except Exception as e:
            raise Exception(f"微信初始化失败: {str(e)}")
    
    def get_new_messages(self) -> Dict[str, List[Dict[str, str]]]:
        """获取并处理新消息"""
        messages_by_sender = {}
        try:
            for target in self.listen_targets:
                try:
                    new_messages = self.wx.GetListenMessage(target)
                    if new_messages:
                        messages_by_sender[target] = [
                            self._process_message(msg)
                            for msg in new_messages
                        ]
                except Exception as e:
                    self.ui.add_message('系统', {
                        'type': '错误',
                        'content': f"获取 {target} 的消息时出错: {str(e)}",
                        'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'id': f'error_get_{target}'
                    })
        except Exception as e:
            self.ui.add_message('系统', {
                'type': '错误',
                'content': f"获取消息时出错: {str(e)}",
                'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'id': 'error_get'
            })
        return messages_by_sender  # 始终返回字典，即使是空的

    def _process_and_print_message(self, msg):
        """处理并打印单条消息"""
        try:
            if hasattr(msg, '__class__') and msg.__class__.__name__ == 'SysMessage':
                msg_type = "系统消息"
                msg_content = str(msg)
                msg_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                msg_id = "系统消息ID"
            else:
                msg_type = msg[0] if isinstance(msg, (list, tuple)) and len(msg) > 0 else "未知类型"
                msg_content = msg[1] if isinstance(msg, (list, tuple)) and len(msg) > 1 else str(msg)
                msg_time = msg[2] if isinstance(msg, (list, tuple)) and len(msg) > 2 else datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                msg_id = msg[-1] if isinstance(msg, (list, tuple)) and len(msg) > 3 else "未知ID"
        except Exception as e:
            msg_type = "处理错误"
            msg_content = f"消息处理错误: {str(e)}, 原始消息: {str(msg)}"
            msg_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            msg_id = "错误ID"
            
        print(f"消息类型: {msg_type}")
        print(f"消息内容: {msg_content}")
        print(f"消息时间: {msg_time}")
        print(f"消息ID: {msg_id}")

    def cleanup(self) -> None:
        """清理监听对象"""
        if self.listen_targets:
            for target in self.listen_targets:
                try:
                    self.wx.RemoveListenChat(target)
                    print(f"已移除监听对象: {target}")
                except Exception as e:
                    print(f"移除监听对象 {target} 失败: {str(e)}")

    def setup_listeners(self) -> List[str]:
        """设置监听对象并返回成功添加的监听对象列表"""
        success_targets = []
        if self.listen_targets:
            for target in self.listen_targets:
                try:
                    self.wx.AddListenChat(target, savepic=True, savefile=True, savevoice=True)
                    success_targets.append(target)
                except Exception as e:
                    if self.ui:
                        self.ui.add_message('系统', {
                            'type': '错误',
                            'content': f"添加监听对象 {target} 失败: {str(e)}",
                            'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'id': f'error_add_listen_{target}'
                        })
        return success_targets
    