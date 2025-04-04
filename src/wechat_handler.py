from wxauto import WeChat
import datetime
import time

import logging
from typing import Dict, List, Optional
import threading

class WeChatHandler:
    def __init__(self, config: dict):
        self.logger = logging.getLogger(__name__)
        self.wx = WeChat()
        self.listen_targets = config.get('listen_targets', [])
        self.start_time = time.time()
        self.ui = None
        self.logger.info("微信处理器初始化完成")
    
    def set_ui(self, ui):
        """设置UI引用"""
        self.ui = ui
        self.logger.debug("UI引用已设置")
    
    def initialize(self) -> str:
        """初始化微信客户端并返回当前登录账号"""
        try:
            nickname = self.wx.nickname  # 使用 nickname 属性获取当前登录账号名称
            self.logger.info(f"微信初始化成功，当前账号: {nickname}")
            return nickname
        except Exception as e:
            self.logger.error(f"微信初始化失败: {str(e)}", exc_info=True)
            raise Exception(f"微信初始化失败: {str(e)}")
    
    def get_new_messages(self) -> Dict[str, List[Dict[str, str]]]:
        """获取并处理新消息"""
        messages_by_sender = {}
        try:
            if not self.listen_targets:
                return messages_by_sender
                
            for target in self.listen_targets:
                try:
                    new_messages = self.wx.GetListenMessage(target)
                    if new_messages:
                        self.logger.info(f"从 {target} 获取到 {len(new_messages)} 条新消息")
                        messages_by_sender[target] = [
                            self._process_message(msg)
                            for msg in new_messages
                        ]
                except Exception as e:
                    self.logger.error(f"获取 {target} 的消息时出错: {str(e)}", exc_info=True)
                    if self.ui:
                        self.ui.add_message('系统', {
                            'type': '错误',
                            'content': f"获取 {target} 的消息时出错: {str(e)}",
                            'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'id': f'error_get_{target}'
                        })
        except Exception as e:
            self.logger.error(f"获取消息时出错: {str(e)}", exc_info=True)
            if self.ui:
                self.ui.add_message('系统', {
                    'type': '错误',
                    'content': f"获取消息时出错: {str(e)}",
                    'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'id': 'error_get'
                })
        return messages_by_sender  # 始终返回字典，即使是空的

    def remove_listener(self, target: str) -> bool:
        """移除监听目标"""
        try:
            self.logger.info(f"尝试移除监听目标: {target}")
            # 先切换到目标聊天
            self.wx.ChatWith(target)
            time.sleep(0.5)  # 等待切换完成
            # 移除监听
            self.wx.RemoveListenChat(target)
            if target in self.listen_targets:
                self.listen_targets.remove(target)
            self.logger.info(f"成功移除监听目标: {target}")
            return True
        except Exception as e:
            self.logger.error(f"移除监听目标 {target} 失败: {str(e)}", exc_info=True)
            if self.ui:
                self.ui.update_status(f'移除监听失败: {str(e)}')
            return False
    
    def cleanup(self):
        """清理所有监听"""
        try:
            self.logger.info("开始清理所有监听目标")
            # 移除所有监听目标
            for target in list(self.listen_targets):
                self.remove_listener(target)
            self.listen_targets.clear()
            self.logger.info("所有监听目标已清理完成")
        except Exception as e:
            self.logger.error(f"清理监听失败: {str(e)}", exc_info=True)
            if self.ui:
                self.ui.update_status(f'清理监听失败: {str(e)}')

    def setup_listeners(self) -> List[str]:
        """设置监听对象并返回成功添加的监听对象列表"""
        success_targets = []
        if not self.listen_targets:
            self.logger.info("未配置监听目标，跳过设置监听")
            return success_targets
            
        self.logger.info(f"开始设置 {len(self.listen_targets)} 个监听目标")
        
        def _setup_listener(target):  # 修改这里，移除self参数
            """设置单个监听目标"""
            try:
                self.logger.info(f"尝试添加监听目标: {target}")
                # 如果UI引用存在，显示提示信息
                if self.ui:
                    self.ui.update_status(f"正在设置监听 {target}，请勿操作微信窗口...")
                
                # 添加监听
                self.wx.AddListenChat(target, savepic=True, savefile=True, savevoice=True)
                
                # 添加到监听列表
                if isinstance(self.listen_targets, set):
                    self.listen_targets.add(target)
                else:
                    if target not in self.listen_targets:
                        self.listen_targets.append(target)
                        
                self.logger.info(f"成功添加监听目标: {target}")
                success_targets.append(target)
                return True
            except Exception as e:
                error_msg = f"添加监听目标 {target} 失败: {str(e)}"
                self.logger.error(error_msg, exc_info=True)
                
                # 显示错误对话框
                if self.ui:
                    from PyQt5.QtWidgets import QMessageBox
                    QMessageBox.warning(
                        self.ui, 
                        "监听设置失败", 
                        f"添加监听目标 {target} 失败\n\n在监听设置过程中，请勿点击或操作微信窗口！\n\n错误详情: {str(e)}"
                    )
                return False

        # 创建并启动所有监听线程
        threads = []
        for target in self.listen_targets:
            # 修改这里，正确传递参数
            thread = threading.Thread(target=_setup_listener, args=(target,), daemon=True)
            thread.start()
            threads.append(thread)
        
        # 等待所有线程完成，但最多等待5秒
        for thread in threads:
            thread.join(timeout=5)
        
        self.logger.info(f"监听设置完成，成功添加 {len(success_targets)} 个目标")
        return success_targets

    def _process_message(self, msg) -> Dict[str, str]:
        """处理单条消息
        
        Args:
            msg: 原始消息对象
            
        Returns:
            处理后的消息字典，包含 type, content, time, id 等字段
        """
        try:
            if hasattr(msg, '__class__') and msg.__class__.__name__ == 'SysMessage':
                return {
                    'type': '系统消息',
                    'content': str(msg),
                    'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'id': f'sys_{time.time()}'
                }
            else:
                return {
                    'type': msg[0] if isinstance(msg, (list, tuple)) and len(msg) > 0 else '文本消息',
                    'content': msg[1] if isinstance(msg, (list, tuple)) and len(msg) > 1 else str(msg),
                    'time': msg[2] if isinstance(msg, (list, tuple)) and len(msg) > 2 else datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'id': msg[-1] if isinstance(msg, (list, tuple)) and len(msg) > 3 else f'msg_{time.time()}'
                }
        except Exception as e:
            self.logger.error(f"消息处理错误: {str(e)}, 原始消息: {str(msg)}", exc_info=True)
            return {
                'type': '处理错误',
                'content': f'消息处理错误: {str(e)}, 原始消息: {str(msg)}',
                'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'id': f'error_{time.time()}'
            }

    def send_message(self, message: str, target: str) -> bool:
        """发送消息到指定目标
        
        Args:
            message: 要发送的消息
            target: 目标聊天对象
            
        Returns:
            bool: 发送是否成功
        """
        try:
            self.logger.info(f"尝试发送消息到 {target}: {message[:50]}{'...' if len(message) > 50 else ''}")
            # 直接使用 SendMsg 方法，通过 who 参数指定接收者
            self.wx.SendMsg(message, who=target)
            self.logger.info(f"成功发送消息到 {target}")
            return True
        except Exception as e:
            self.logger.error(f"发送消息到 {target} 失败: {str(e)}", exc_info=True)
            if self.ui:
                self.ui.add_message('系统', {
                    'type': 'Text',
                    'content': f'已连接到微信账号: {nickname}',
                    'time': datetime.now()
                })  # 添加这个右花括号和括号来关闭字典和方法调用
                    # 在第229行附近，可能是一个字典定义
                    # 原来的代码可能是这样的：
                self.ui.add_message('系统', {
                    'type': 'Text',
                    'content': f'发送消息失败: {str(e)}',
                    'time': datetime.now(),
                'id': f'error_send_{time.time()}'
                })

                # 修改为正确的缩进：
                self.ui.add_message('系统', {
                    'type': 'Text',
                    'content': f'发送消息失败: {str(e)}',
                    'time': datetime.now(),
                    'id': f'error_send_{time.time()}'

                })
                    
