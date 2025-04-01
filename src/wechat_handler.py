from wxauto import *
import time
import datetime

class WeChatHandler:
    def __init__(self, config: dict):
        self.wx = WeChat()
        self.listen_targets = config.get('listen_targets', [])
        self.start_time = time.time()
        print(f"微信客户端初始化成功，当前登录账号：{self.wx.nickname}")
    
    def initialize(self) -> str:
        """初始化微信客户端并返回当前登录账号"""
        return self.wx.nickname
    
    def setup_listeners(self) -> None:
        """设置消息监听"""
        if self.listen_targets:
            print(f"已设置指定监听对象: {', '.join(self.listen_targets)}")
            for target in self.listen_targets:
                try:
                    self.wx.AddListenChat(target, savepic=True, savefile=True, savevoice=True)
                    print(f"成功添加监听对象: {target}")
                except Exception as e:
                    print(f"添加监听对象 {target} 失败: {str(e)}")
        else:
            print("当前监听所有聊天对象")
        
        print(f"开始监听新消息: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
        print("请在其他设备上向当前微信账号发送消息...")
        print("-" * 50)

    def get_new_messages(self) -> None:
        """获取并处理新消息"""
        try:
            for target in self.listen_targets:
                new_messages = self.wx.GetListenMessage(target)
                
                if new_messages:
                    current_time = time.time()
                    elapsed_time = current_time - self.start_time
                    
                    print(f"\n接收到来自 {target} 的新消息:")
                    print(f"接收时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
                    print(f"监听延迟: {elapsed_time:.3f} 秒")
                    
                    for msg in new_messages:
                        self._process_and_print_message(msg)
                    print("-" * 50)
                    self.start_time = current_time

        except Exception as e:
            print(f"获取消息时出错: {str(e)}")

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
    