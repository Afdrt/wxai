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
        self.last_check_time = time.time()
        self.check_interval = 60  # 每60秒检查一次监听状态
        self.message_cache = {}  # 用于消息去重
        
    def initialize(self) -> str:
        """初始化微信客户端并返回当前登录账号"""
        return self.wx.nickname
    
    def _check_window_state(self) -> bool:
        """检查微信窗口状态"""
        try:
            # 尝试获取会话列表来验证窗口状态
            sessions = self.wx.GetSessionList()
            return bool(sessions)
        except Exception as e:
            print(f"[AI流程] 微信窗口状态检查失败: {str(e)}")
            return False

    def _setup_single_listener(self, target: str, max_retries: int = 3, retry_delay: int = 2) -> bool:
        """设置单个监听对象"""
        for attempt in range(max_retries):
            try:
                if not self._check_window_state():
                    raise Exception("微信窗口状态异常")
                
                # 尝试切换到目标聊天
                self.wx.ChatWith(target)
                time.sleep(0.5)  # 等待聊天窗口加载
                
                # 验证是否成功切换到目标聊天
                current_chat = self.wx.GetCurrentChatName()
                if not current_chat or target not in current_chat:
                    raise Exception(f"切换到目标聊天失败: {target}")
                
                # 添加监听
                self.wx.AddListenChat(
                    target,
                    savepic=self.save_media.get('savepic', True),
                    savefile=self.save_media.get('savefile', True),
                    savevoice=self.save_media.get('savevoice', True)
                )
                print(f"[AI流程] 成功添加监听对象: {target}")
                return True
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"[AI流程] 添加监听对象 {target} 失败 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
                    time.sleep(retry_delay)
                else:
                    print(f"[AI流程] 添加监听对象 {target} 最终失败: {str(e)}")
        return False

    def setup_listeners(self) -> List[str]:
        """设置消息监听，包含重试机制"""
        success_targets = []
        
        if self.listen_targets:
            for target in self.listen_targets:
                if self._setup_single_listener(target):
                    success_targets.append(target)
                    self.message_cache[target] = set()  # 初始化消息缓存
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
    
    def _check_and_restore_listeners(self) -> None:
        """检查并恢复监听状态"""
        current_time = time.time()
        if current_time - self.last_check_time >= self.check_interval:
            self.last_check_time = current_time
            if not self._check_window_state():
                print("[AI流程] 检测到微信窗口状态异常，尝试恢复监听...")
                self.setup_listeners()

    def _is_duplicate_message(self, target: str, msg_id: str) -> bool:
        """检查是否为重复消息"""
        if msg_id in self.message_cache[target]:
            return True
        self.message_cache[target].add(msg_id)
        # 保持缓存大小在合理范围
        if len(self.message_cache[target]) > 1000:
            self.message_cache[target] = set(list(self.message_cache[target])[-500:])
        return False

    def get_new_messages(self) -> Dict[str, List[Dict[str, str]]]:
        """获取新消息"""
        try:
            self._check_and_restore_listeners()
            messages_by_sender = {}
            
            if self.listen_targets:
                for target in self.listen_targets:
                    try:
                        new_messages = self.wx.GetListenMessage(target)
                        if new_messages:
                            print(f"[AI流程] 从{target}接收到{len(new_messages)}条新消息")
                            # 过滤掉AI自己发送的消息和重复消息
                            filtered_messages = [
                                msg_dict for msg in new_messages 
                                if not (isinstance(msg, (list, tuple)) and len(msg) > 3 and msg[3] == 'AI')
                                and (msg_dict := self.process_message(msg))
                                and not self._is_duplicate_message(target, msg_dict['id'])
                            ]
                            if filtered_messages:
                                print(f"[AI流程] 过滤后剩余{len(filtered_messages)}条有效消息")
                                messages_by_sender[target] = filtered_messages
                    except Exception as e:
                        print(f"[AI流程] 获取{target}的消息时出错: {str(e)}")
            else:
                try:
                    new_msg = self.wx.GetNextNewMessage(
                        savepic=self.save_media.get('savepic', True),
                        savefile=self.save_media.get('savefile', True),
                        savevoice=self.save_media.get('savevoice', True)
                    )
                    if new_msg:
                        for chat_name, messages in new_msg.items():
                            filtered_messages = [
                                msg_dict for msg in messages 
                                if not (isinstance(msg, (list, tuple)) and len(msg) > 3 and msg[3] == 'AI')
                                and (msg_dict := self.process_message(msg))
                            ]
                            if filtered_messages:
                                messages_by_sender[chat_name] = filtered_messages
                except Exception as e:
                    print(f"[AI流程] 获取新消息时出错: {str(e)}")
            
            return messages_by_sender
        except Exception as e:
            print(f"[AI流程] 获取消息过程中发生错误: {str(e)}")
            return {}
    
    def send_message(self, content: str, target: str) -> bool:
        """发送消息到指定目标"""
        try:
            # 添加AI标记作为第四个参数
            print(f"[AI流程] 正在准备向{target}发送AI回复")
            print(f"[AI流程] 回复内容: {content}")
            self.wx.SendMsg(content, who=target, extra='AI')
            print(f"[AI流程] 成功向{target}发送AI回复")
            return True
        except Exception as e:
            print(f"[AI流程] 向 {target} 发送消息失败: {str(e)}")
            return False
    
    def cleanup(self) -> None:
        """清理监听对象"""
        if self.listen_targets:
            for target in self.listen_targets:
                try:
                    self.wx.RemoveListenChat(target)
                except Exception as e:
                    print(f"移除监听对象 {target} 失败: {str(e)}")
    