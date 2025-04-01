import sys
import time
from collections import deque
from datetime import datetime, timedelta
from typing import Optional
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QTextCursor
from src.config import WECHAT_CONFIG, AI_CONFIG, UI_CONFIG
from src.wechat_handler import WeChatHandler
from src.ai_handler import AIHandler
from src.ui import ChatWindow
from src.message_cache import MessageCache

# 注册 QTextCursor 类型
from PyQt5.QtCore import QMetaType
QMetaType.type("QTextCursor")

from src.message_cache import MessageCache

class MessageMonitor(QThread):
    message_received = pyqtSignal(str, dict)  # 添加这行
    status_updated = pyqtSignal(str)  # 添加这行
    
    def __init__(self, wechat_handler: WeChatHandler, ai_handler: AIHandler):
        super().__init__()
        self.wechat = wechat_handler
        self.ai = ai_handler
        self.running = False
        self.message_cache = MessageCache()
        
    def check_and_process_messages(self):
        """检查并处理所有用户的缓存消息"""
        for sender in list(self.message_cache.user_messages.keys()):
            combined_message = self.message_cache.get_combined_messages(sender)
            if combined_message:
                try:
                    self.status_updated.emit(f'开始处理来自 {sender} 的消息组合')
                    prompt = f"用户发送了以下多条消息：\n{combined_message}\n请统一回复这些消息。"
                    self.status_updated.emit(f'发送到AI的消息: {prompt}')
                    
                    ai_response = self.ai.process_message(prompt)
                    if ai_response:
                        self.status_updated.emit(f'收到AI回复: {ai_response}')
                        if self.wechat.send_message(ai_response, sender):
                            self.status_updated.emit(f'已成功发送回复到 {sender}')
                            self.message_received.emit('AI助手', {
                                'type': 'Text',
                                'content': ai_response,
                                'time': datetime.now(),
                                'id': 'ai_response'
                            })
                        else:
                            self.status_updated.emit(f'发送消息到 {sender} 失败')
                except Exception as e:
                    self.status_updated.emit(f'AI处理失败: {str(e)}')

    def run(self):
        self.running = True
        while self.running:
            try:
                # 处理新消息
                messages = self.wechat.get_new_messages()
                for sender, msg_list in messages.items():
                    for msg in msg_list:
                        self.message_received.emit(sender, msg)
                        
                        if msg['type'] == 'Text' or msg['type'] == '文本消息':
                            if sender == 'AI助手' or msg.get('id') == 'ai_response':
                                continue
                            
                            if not self.wechat.ui.is_auto_reply_enabled():
                                continue
                            
                            self.message_cache.add_message(sender, msg['content'])
                            self.status_updated.emit(f'已缓存来自 {sender} 的消息: {msg["content"]}')
                
                # 定期检查是否有需要处理的消息
                self.check_and_process_messages()
                
            except Exception as e:
                self.status_updated.emit(f'监听出错: {str(e)}')
            
            time.sleep(0.1)
    
    def stop(self):
        self.running = False

class MainApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = ChatWindow(UI_CONFIG)
        self.wechat = None
        self.ai = None
        self.monitor = None
        
        self.setup_handlers()
    
    def setup_handlers(self):
        self.window.set_start_handler(self.start_monitoring)
        self.window.set_stop_handler(self.stop_monitoring)
    
    def start_monitoring(self):
        try:
            # 获取最新配置
            config = self.window.get_config()
            if not config['api_key']:
                self.window.update_status('错误: 请设置API Key')
                return
            
            # 更新配置
            AI_CONFIG['api_key'] = config['api_key']
            if config['listen_targets']:
                WECHAT_CONFIG['listen_targets'] = config['listen_targets']
            
            # 初始化处理器
            self.wechat = WeChatHandler(WECHAT_CONFIG)
            self.wechat.set_ui(self.window)  # 添加这行，设置UI引用
            self.ai = AIHandler(AI_CONFIG)
            
            # 初始化微信
            nickname = self.wechat.initialize()
            self.window.update_status(f'已连接微信账号: {nickname}')
            
            # 设置监听
            success_targets = self.wechat.setup_listeners()
            if success_targets:
                self.window.update_status(f'正在监听: {", ".join(success_targets)}')
            else:
                self.window.update_status('监听所有聊天对象')
            
            # 启动监控
            self.monitor = MessageMonitor(self.wechat, self.ai)
            self.monitor.message_received.connect(self.window.add_message)
            self.monitor.status_updated.connect(self.window.update_status)
            self.monitor.start()
            
            # 更新UI状态
            self.window.set_running_state(True)
            
        except Exception as e:
            self.window.update_status(f'启动失败: {str(e)}')
    
    def stop_monitoring(self):
        if self.monitor:
            self.monitor.stop()
            self.monitor.wait()
        
        if self.wechat:
            self.wechat.cleanup()
        
        self.window.set_running_state(False)
        self.window.update_status('监听已停止')
    
    def run(self):
        self.window.show()
        return self.app.exec_()

if __name__ == '__main__':
    app = MainApp()
    sys.exit(app.run())