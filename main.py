import sys
import time
from collections import deque
from datetime import datetime, timedelta
from typing import Optional
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QtCriticalMsg, QtWarningMsg, QtFatalMsg, qInstallMessageHandler
from PyQt5.QtGui import QTextCursor
import pywintypes  # 添加这一行
from src.config import WECHAT_CONFIG, AI_CONFIG, UI_CONFIG
from src.wechat_handler import WeChatHandler
from src.ai_handler import AIHandler
from src.ui import ChatWindow
from src.message_cache import MessageCache
from src.logger import setup_logger
from src.exception_handler import GlobalExceptionHandler, setup_thread_exception_hook
import logging

# 初始化日志系统
logger = setup_logger()

# 安装全局异常处理器
exception_handler = GlobalExceptionHandler(logger)
exception_handler.install()

# 设置线程异常钩子
setup_thread_exception_hook()

# 注册 QTextCursor 类型
from PyQt5.QtCore import QMetaType
QMetaType.type("QTextCursor")

from src.message_cache import MessageCache

class MessageMonitor(QThread):
    message_received = pyqtSignal(str, dict)  # 添加这行
    status_updated = pyqtSignal(str)  # 添加这行
    
    def __init__(self, wechat_handler: WeChatHandler, ai_handler: AIHandler):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.wechat = wechat_handler
        self.ai = ai_handler
        self.running = False
        self.message_cache = MessageCache()
        self.last_ai_responses = {}  # 记录每个用户最近3次AI的回复
        self.listen_targets = set()  # 添加监听目标集合
        self.logger.info("消息监控器初始化完成")

    def update_listen_targets(self, targets):
        """更新监听目标列表"""
        self.listen_targets = set(targets)
        self.logger.info(f"更新监听目标: {', '.join(targets)}")

    def check_and_process_messages(self):
        """检查并处理所有用户的缓存消息"""
        for sender in list(self.message_cache.user_messages.keys()):
            combined_message = self.message_cache.get_combined_messages(sender)
            if combined_message:
                try:
                    status_msg = f'开始处理来自 {sender} 的消息组合'
                    self.logger.info(status_msg)
                    self.status_updated.emit(status_msg)
                    
                    prompt = f"用户发送了以下多条消息：\n{combined_message}\n请统一回复这些消息。"
                    self.logger.debug(f'发送到AI的消息: {prompt}')
                    self.status_updated.emit(f'发送到AI的消息: {prompt}')
                    
                    ai_response = self.ai.process_message(prompt)
                    if ai_response:
                        # 保存AI的回复到历史记录
                        if sender not in self.last_ai_responses:
                            self.last_ai_responses[sender] = []
                        self.last_ai_responses[sender].append(ai_response)
                        if len(self.last_ai_responses[sender]) > 3:
                            self.last_ai_responses[sender].pop(0)  # 保持最近3条记录
                            
                        self.logger.info(f'收到AI回复: {ai_response[:100]}{"..." if len(ai_response) > 100 else ""}')
                        self.status_updated.emit(f'收到AI回复: {ai_response}')
                        
                        if self.wechat.send_message(ai_response, sender):
                            self.logger.info(f'已成功发送回复到 {sender}')
                            self.status_updated.emit(f'已成功发送回复到 {sender}')
                            self.message_received.emit('AI助手', {
                                'type': 'Text',
                                'content': ai_response,
                                'time': datetime.now(),
                                'id': 'ai_response'
                            })
                        else:
                            self.logger.error(f'发送消息到 {sender} 失败')
                            self.status_updated.emit(f'发送消息到 {sender} 失败')
                except Exception as e:
                    self.logger.error(f'AI处理失败: {str(e)}', exc_info=True)
                    self.status_updated.emit(f'AI处理失败: {str(e)}')

    def run(self):
        self.logger.info("消息监控线程启动")
        self.running = True
        while self.running:
            try:
                messages = self.wechat.get_new_messages()
                for sender, msg_list in messages.items():
                    # 只处理在监听列表中的目标消息
                    if self.listen_targets and sender not in self.listen_targets:
                        self.logger.debug(f"跳过非监听目标 {sender} 的消息")
                        continue
                        
                    for msg in msg_list:
                        self.logger.info(f"收到来自 {sender} 的消息: {msg.get('content', '')[:100]}")
                        self.message_received.emit(sender, msg)
                        
                        if msg['type'] == 'Text' or msg['type'] == '文本消息':
                            if sender == 'AI助手' or msg.get('id') == 'ai_response':
                                self.logger.debug("跳过AI助手自己的消息")
                                continue
                            
                            if not self.wechat.ui.is_auto_reply_enabled():
                                self.logger.debug("自动回复已禁用，跳过处理")
                                continue
                            
                            # 检查消息内容是否在最近3次AI回复中
                            content = msg.get('content', '')
                            if sender in self.last_ai_responses and content in self.last_ai_responses[sender]:
                                self.logger.info(f'跳过缓存AI回复内容: {content[:50]}{"..." if len(content) > 50 else ""}')
                                self.status_updated.emit(f'跳过缓存AI回复内容: {content}')
                                continue
                            
                            # 缓存消息
                            self.message_cache.add_message(sender, content)
                            self.logger.info(f'已缓存来自 {sender} 的消息: {content[:50]}{"..." if len(content) > 50 else ""}')
                            self.status_updated.emit(f'已缓存来自 {sender} 的消息: {content}')
                
                # 定期检查是否有需要处理的消息
                self.check_and_process_messages()
                
            except Exception as e:
                self.logger.error(f'监听出错: {str(e)}', exc_info=True)
                self.status_updated.emit(f'监听出错: {str(e)}')
            
            time.sleep(0.1)
    
    def stop(self):
        self.logger.info("停止消息监控线程")
        self.running = False

class MainApp:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("初始化主应用程序")
        self.app = QApplication(sys.argv)
        
        # 设置Qt异常处理
        def qt_message_handler(mode, context, message):
            if mode == QtCriticalMsg:
                logger.critical(f"Qt错误: {message}")
            elif mode == QtWarningMsg:
                logger.warning(f"Qt警告: {message}")
            elif mode == QtFatalMsg:
                logger.critical(f"Qt致命错误: {message}")
            
        qInstallMessageHandler(qt_message_handler)
        
        self.window = ChatWindow(UI_CONFIG)
        
        # 提前初始化微信处理器
        self.logger.info("提前初始化微信处理器")
        try:
            self.wechat = WeChatHandler(WECHAT_CONFIG)
            self.wechat.set_ui(self.window)
        except Exception as e:
            self.logger.error(f"微信处理器初始化失败: {str(e)}", exc_info=True)
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(None, "错误", "微信未打开或无法访问，请先打开微信并确保已登录。")
            sys.exit(1)
        
        # 提前初始化AI处理器
        self.logger.info("提前初始化AI处理器")
        self.ai = AIHandler(AI_CONFIG)
        
        # 尝试连接微信客户端
        try:
            self.logger.info("尝试连接微信客户端")
            nickname = self.wechat.initialize()
            self.logger.info(f"已连接微信账号: {nickname}")
            self.window.update_status(f'已连接微信账号: {nickname}')
        except Exception as e:
            self.logger.error(f"微信初始化失败: {str(e)}", exc_info=True)
            self.window.update_status(f'微信初始化失败: {str(e)}，请确保微信已登录')
        
        self.monitor = None
        
        self.setup_handlers()
    
    # 在 MainApp 类的 setup_handlers 方法中添加以下代码
    
    def setup_handlers(self):
        self.window.set_start_handler(self.start_monitoring)
        self.window.set_stop_handler(self.stop_monitoring)
        # 添加监听和取消监听的处理器
        self.window.set_add_listener_handler(self.add_single_listener)
        self.window.set_remove_listener_handler(self.remove_single_listener)
        self.logger.info("设置UI事件处理器完成")
    
    # 添加以下方法到 MainApp 类
    
    def add_single_listener(self, target):
        """添加单个监听目标"""
        if not self.wechat:
            self.window.update_status(f"无法添加监听: {target}，微信处理器未初始化")
            return
            
        try:
            self.window.update_status(f"正在添加监听目标: {target}...")
            success = self.wechat.add_listener(target)
            if success:
                self.window.update_status(f"成功添加监听目标: {target}")
                # 更新监控器的监听目标
                if self.monitor:
                    self.monitor.update_listen_targets(self.wechat.listen_targets)
            else:
                self.window.update_status(f"添加监听目标失败: {target}")
        except Exception as e:
            self.logger.error(f"添加监听目标异常: {str(e)}", exc_info=True)
            self.window.update_status(f"添加监听出错: {str(e)}")
    
    def remove_single_listener(self, target):
        """移除单个监听目标"""
        if not self.wechat:
            self.window.update_status(f"无法移除监听: {target}，微信处理器未初始化")
            return
            
        try:
            self.window.update_status(f"正在移除监听目标: {target}...")
            success = self.wechat.remove_listener(target)
            if success:
                self.window.update_status(f"成功移除监听目标: {target}")
                # 更新监控器的监听目标
                if self.monitor:
                    self.monitor.update_listen_targets(self.wechat.listen_targets)
            else:
                self.window.update_status(f"移除监听目标失败: {target}")
        except Exception as e:
            self.logger.error(f"移除监听目标异常: {str(e)}", exc_info=True)
            self.window.update_status(f"移除监听出错: {str(e)}")
    
    def start_monitoring(self):
        try:
            self.logger.info("开始启动监控")
            # 获取最新配置
            config = self.window.get_config()
            if not config['api_key']:
                self.logger.error("API Key未设置")
                self.window.update_status('错误: 请设置API Key')
                return
            
            # 更新配置
            AI_CONFIG.update({
                'api_key': config['api_key'],
                'service': config['service'],
                'model': config['model'],
                'system_prompt': config['ai_behavior']['system_prompt'],
                'temperature': config['ai_behavior']['temperature'],
                'max_tokens': config['ai_behavior']['max_tokens'],
                # 添加缺失的配置项
                'presence_penalty': config['ai_behavior']['presence_penalty'],
                'frequency_penalty': config['ai_behavior']['frequency_penalty'],
                'top_p': config['ai_behavior']['top_p']
            })
            
            # 检查微信是否已初始化，如果没有或者出错，尝试重新初始化
            if not self.wechat or not hasattr(self.wechat, 'wx') or not self.wechat.wx:
                self.logger.info("微信未初始化或已失效，尝试重新初始化")
                self.wechat = WeChatHandler(WECHAT_CONFIG)
                self.wechat.set_ui(self.window)
                nickname = self.wechat.initialize()
                self.logger.info(f"已重新连接微信账号: {nickname}")
                self.window.update_status(f'已重新连接微信账号: {nickname}')
            
            # 更新微信配置
            if config['listen_targets']:
                WECHAT_CONFIG['listen_targets'] = config['listen_targets']
                self.wechat.listen_targets = config['listen_targets']
            
            # 更新AI处理器配置
            self.ai.update_config(AI_CONFIG)
            
            # 先创建监控实例
            self.logger.info("创建消息监控器")
            self.monitor = MessageMonitor(self.wechat, self.ai)
            self.monitor.message_received.connect(self.window.add_message)
            self.monitor.status_updated.connect(self.window.update_status)
            
            # 设置监听前显示提示
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(
                self.window,
                "监听设置提示",
                "即将设置微信监听，在此过程中请勿点击或操作微信窗口，否则可能导致监听设置失败。"
            )
            
            # 创建一个单独的线程来设置监听，避免UI卡死
            class SetupListenerThread(QThread):
                finished = pyqtSignal(list)  # 添加信号，用于返回成功的监听目标
                error = pyqtSignal(str)  # 添加错误信号
                status = pyqtSignal(str)  # 添加状态更新信号
                
                def __init__(self, wechat_handler):
                    super().__init__()
                    self.logger = logging.getLogger(__name__)
                    self.wechat = wechat_handler
                    
                def run(self):
                    try:
                        # 设置监听
                        self.logger.info("线程开始设置微信监听")
                        success_targets = self.wechat.setup_listeners()
                        self.logger.info(f"线程成功设置监听: {success_targets}")
                        self.finished.emit(success_targets)
                    except Exception as e:
                        self.logger.error(f"线程设置监听失败: {str(e)}", exc_info=True)
                        self.error.emit(f"设置监听失败: {str(e)}")
                        # 即使失败也要发送空列表，确保主线程能继续执行
                        self.finished.emit([])
            
            # 创建并启动监听设置线程
            self.logger.info("创建监听设置线程")
            self.setup_thread = SetupListenerThread(self.wechat)
            
            # 连接信号，处理监听设置完成后的操作
            def on_setup_finished(success_targets):
                if success_targets:
                    self.logger.info(f"成功监听目标: {', '.join(success_targets)}")
                    self.window.update_status(f'正在监听: {", ".join(success_targets)}')
                    # 更新监听目标
                    self.monitor.update_listen_targets(success_targets)
                else:
                    self.logger.info("未设置特定监听目标或设置失败，监听所有聊天")
                    self.window.update_status('监听所有聊天对象')
                
                # 启动监控
                self.logger.info("启动消息监控线程")
                self.monitor.start()
                
                # 更新UI状态
                self.window.set_running_state(True)
                self.logger.info("监控已成功启动")
            
            # 处理错误信号
            def on_setup_error(error_msg):
                from PyQt5.QtWidgets import QMessageBox
                self.logger.error(f"监听设置错误: {error_msg}")
                # 使用 QMetaObject.invokeMethod 确保在主线程中显示对话框
                QMessageBox.warning(
                    self.window,
                    "监听设置警告",
                    f"部分监听目标设置失败: {error_msg}\n\n程序将继续运行，但部分功能可能受限。"
                )
            
            self.setup_thread.finished.connect(on_setup_finished)
            self.setup_thread.error.connect(on_setup_error)
            
            # 设置监听
            self.logger.info("设置微信监听")
            self.window.update_status("正在设置微信监听，请稍候...")
            self.setup_thread.start()
            
        except Exception as e:
            self.logger.error(f"启动监控失败: {str(e)}", exc_info=True)
            self.window.update_status(f'启动失败: {str(e)}')
    
    def stop_monitoring(self):
        self.logger.info("停止监控")
        self.window.update_status('正在停止监听，请稍候...')
        
        # 创建一个停止监听的线程
        class StopMonitorThread(QThread):
            finished = pyqtSignal()
            status = pyqtSignal(str)
            
            def __init__(self, monitor, wechat):
                super().__init__()
                self.logger = logging.getLogger(__name__)
                self.monitor = monitor
                self.wechat = wechat
                
            def run(self):
                try:
                    if self.monitor:
                        self.status.emit("正在停止消息监控...")
                        self.logger.info("停止消息监控线程")
                        self.monitor.stop()
                        self.monitor.wait(3000)  # 修改这里，直接传入毫秒值
                        self.logger.info("消息监控线程已停止")
                    
                    if self.wechat:
                        self.status.emit("正在清理微信监听...")
                        self.logger.info("清理微信监听")
                        self.wechat.cleanup()
                        self.logger.info("微信监听已清理")
                    
                    self.status.emit('监听已停止')
                    self.finished.emit()
                except Exception as e:
                    self.logger.error(f"停止监控时出错: {str(e)}", exc_info=True)
                    self.status.emit(f'停止监控时出错: {str(e)}')
                    self.finished.emit()
        
        # 创建并启动停止线程
        self.stop_thread = StopMonitorThread(self.monitor, self.wechat)
        
        # 连接信号
        def on_stop_finished():
            self.window.set_running_state(False)
            self.logger.info("监控已完全停止")
            # 修改这里：不要将wechat设为None，只将monitor设为None
            self.monitor = None
            # self.wechat = None  # 注释掉这行，保留wechat实例
        
        self.stop_thread.finished.connect(on_stop_finished)
        self.stop_thread.status.connect(self.window.update_status)
        
        # 禁用开始/停止按钮，避免重复点击
        self.window.set_buttons_enabled(False)
        
        # 启动停止线程
        self.stop_thread.start()
    
    def run(self):
        self.logger.info("显示主窗口")
        self.window.show()
        self.logger.info("进入应用程序主循环")
        return self.app.exec_()

if __name__ == '__main__':
    try:
        logger.info("=== 微信AI助手启动 ===")
        try:
            app = MainApp()
            exit_code = app.run()
            logger.info(f"=== 微信AI助手退出，退出码: {exit_code} ===")
            sys.exit(exit_code)
        except pywintypes.error as e:
            if e.winerror == 1400:  # 无效的窗口句柄
                from PyQt5.QtWidgets import QMessageBox
                logger.error("微信未打开或无法访问", exc_info=True)
                QMessageBox.critical(None, "错误", "微信未打开或无法访问，请先打开微信并确保已登录。")
                sys.exit(1)
            raise  # 重新抛出其他类型的pywintypes错误
    except Exception as e:
        logger.critical(f"程序崩溃: {str(e)}", exc_info=True)
        sys.exit(1)