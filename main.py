import sys
import time
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread, pyqtSignal
from src.config import WECHAT_CONFIG, AI_CONFIG, UI_CONFIG
from src.wechat_handler import WeChatHandler
from src.ai_handler import AIHandler
from src.ui import ChatWindow

class MessageMonitor(QThread):
    message_received = pyqtSignal(str, dict)
    status_updated = pyqtSignal(str)
    
    def __init__(self, wechat_handler: WeChatHandler, ai_handler: AIHandler):
        super().__init__()
        self.wechat = wechat_handler
        self.ai = ai_handler
        self.running = False
    
    def run(self):
        self.running = True
        while self.running:
            try:
                messages = self.wechat.get_new_messages()
                for sender, msg_list in messages.items():
                    for msg in msg_list:
                        self.message_received.emit(sender, msg)
                        
                        # 处理文本消息
                        if msg['type'] == 'Text' or msg['type'] == '文本消息':
                            # 增加判断，跳过AI自己发送的消息
                            if sender == 'AI助手' or msg.get('id') == 'ai_response':
                                continue
                            
                            # 检查AI回复开关是否打开
                            if not self.wechat.ui.is_auto_reply_enabled():
                                continue
                                
                            try:
                                # 获取AI响应
                                ai_response = self.ai.process_message(msg['content'])
                                if ai_response:
                                    # 发送AI响应
                                    if self.wechat.send_message(ai_response, sender):
                                        self.message_received.emit('AI助手', {
                                            'type': 'Text',
                                            'content': ai_response,
                                            'time': msg['time'],
                                            'id': 'ai_response'
                                        })
                                    else:
                                        self.status_updated.emit(f'发送消息到 {sender} 失败')
                            except Exception as e:
                                self.status_updated.emit(f'AI处理失败: {str(e)}')
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