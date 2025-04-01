import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox, simpledialog
import threading
import os
import time
from wxauto import WeChat

class WeChatTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("微信自动化测试工具")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        # 初始化微信实例变量
        self.wx = None
        self.is_initialized = False
        
        # 创建主框架
        self.create_main_frame()
        
        # 创建状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("状态: 未初始化微信实例")
        self.status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def create_main_frame(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建左侧功能区
        left_frame = ttk.Frame(main_frame, width=900)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # 创建右侧输出区
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建选项卡
        tab_control = ttk.Notebook(left_frame)
        
        # 基本操作选项卡
        basic_tab = ttk.Frame(tab_control)
        tab_control.add(basic_tab, text="基本操作")
        self.create_basic_tab(basic_tab)
        
        # 聊天功能选项卡
        chat_tab = ttk.Frame(tab_control)
        tab_control.add(chat_tab, text="聊天功能")
        self.create_chat_tab(chat_tab)
        
        # 消息获取选项卡
        message_tab = ttk.Frame(tab_control)
        tab_control.add(message_tab, text="消息获取")
        self.create_message_tab(message_tab)
        
        # 联系人管理选项卡
        contact_tab = ttk.Frame(tab_control)
        tab_control.add(contact_tab, text="联系人管理")
        self.create_contact_tab(contact_tab)
        
        # 文件管理选项卡
        file_tab = ttk.Frame(tab_control)
        tab_control.add(file_tab, text="文件管理")
        self.create_file_tab(file_tab)
        
        tab_control.pack(expand=True, fill=tk.BOTH)
        
        # 创建输出区
        output_label = ttk.Label(right_frame, text="输出结果:")
        output_label.pack(anchor=tk.W, padx=5, pady=5)
        
        self.output_text = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD, width=60, height=30)
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 清除输出按钮
        clear_button = ttk.Button(right_frame, text="清除输出", command=self.clear_output)
        clear_button.pack(anchor=tk.E, padx=5, pady=5)
    
    def create_basic_tab(self, parent):
        # 初始化微信实例
        init_frame = ttk.LabelFrame(parent, text="初始化微信实例")
        init_frame.pack(fill=tk.X, padx=5, pady=5)
        
        language_frame = ttk.Frame(init_frame)
        language_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(language_frame, text="语言:").pack(side=tk.LEFT, padx=5)
        self.language_var = tk.StringVar(value="cn")
        language_combo = ttk.Combobox(language_frame, textvariable=self.language_var, width=10)
        language_combo['values'] = ('cn', 'cn_t', 'en')
        language_combo.pack(side=tk.LEFT, padx=5)
        
        debug_frame = ttk.Frame(init_frame)
        debug_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.debug_var = tk.BooleanVar(value=False)
        debug_check = ttk.Checkbutton(debug_frame, text="调试模式", variable=self.debug_var)
        debug_check.pack(side=tk.LEFT, padx=5)
        
        init_button = ttk.Button(init_frame, text="初始化微信实例", command=self.initialize_wechat)
        init_button.pack(fill=tk.X, padx=5, pady=5)
        
        # 窗口操作
        window_frame = ttk.LabelFrame(parent, text="窗口操作")
        window_frame.pack(fill=tk.X, padx=5, pady=5)
        
        show_button = ttk.Button(window_frame, text="显示微信窗口", command=lambda: self.run_function(self._show_wechat))
        show_button.pack(fill=tk.X, padx=5, pady=5)
        
        refresh_button = ttk.Button(window_frame, text="刷新微信窗口", command=lambda: self.run_function(self._refresh_wechat))
        refresh_button.pack(fill=tk.X, padx=5, pady=5)
        
        # 界面切换
        switch_frame = ttk.LabelFrame(parent, text="界面切换")
        switch_frame.pack(fill=tk.X, padx=5, pady=5)
        
        switch_chat_button = ttk.Button(switch_frame, text="切换到聊天页面", command=lambda: self.run_function(self._switch_to_chat))
        switch_chat_button.pack(fill=tk.X, padx=5, pady=5)
        
        switch_contact_button = ttk.Button(switch_frame, text="切换到通讯录页面", command=lambda: self.run_function(self._switch_to_contact))
        switch_contact_button.pack(fill=tk.X, padx=5, pady=5)
    
    def create_chat_tab(self, parent):
        # 切换聊天对象
        chat_with_frame = ttk.LabelFrame(parent, text="切换聊天对象")
        chat_with_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(chat_with_frame, text="聊天对象:").pack(anchor=tk.W, padx=5, pady=2)
        self.chat_with_entry = ttk.Entry(chat_with_frame)
        self.chat_with_entry.pack(fill=tk.X, padx=5, pady=2)
        
        chat_with_button = ttk.Button(chat_with_frame, text="切换聊天对象", command=self.chat_with)
        chat_with_button.pack(fill=tk.X, padx=5, pady=5)
        
        # 发送消息
        send_msg_frame = ttk.LabelFrame(parent, text="发送消息")
        send_msg_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(send_msg_frame, text="消息内容:").pack(anchor=tk.W, padx=5, pady=2)
        self.msg_text = scrolledtext.ScrolledText(send_msg_frame, wrap=tk.WORD, width=30, height=5)
        self.msg_text.pack(fill=tk.X, padx=5, pady=2)
        
        at_frame = ttk.Frame(send_msg_frame)
        at_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(at_frame, text="@成员 (用逗号分隔):").pack(side=tk.LEFT, padx=5)
        self.at_entry = ttk.Entry(at_frame)
        self.at_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        send_msg_button = ttk.Button(send_msg_frame, text="发送消息", command=self.send_message)
        send_msg_button.pack(fill=tk.X, padx=5, pady=5)
        
        at_all_button = ttk.Button(send_msg_frame, text="@所有人", command=self.at_all)
        at_all_button.pack(fill=tk.X, padx=5, pady=5)
        
        # 发送文件
        send_file_frame = ttk.LabelFrame(parent, text="发送文件")
        send_file_frame.pack(fill=tk.X, padx=5, pady=5)
        
        file_select_frame = ttk.Frame(send_file_frame)
        file_select_frame.pack(fill=tk.X, padx=5, pady=2)
        
        self.file_path_var = tk.StringVar()
        file_path_entry = ttk.Entry(file_select_frame, textvariable=self.file_path_var)
        file_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=2)
        
        browse_button = ttk.Button(file_select_frame, text="浏览", command=self.browse_file)
        browse_button.pack(side=tk.RIGHT, padx=5, pady=2)
        
        send_file_button = ttk.Button(send_file_frame, text="发送文件", command=self.send_file)
        send_file_button.pack(fill=tk.X, padx=5, pady=5)
    
    def create_message_tab(self, parent):
        # 获取消息
        get_msg_frame = ttk.LabelFrame(parent, text="获取消息")
        get_msg_frame.pack(fill=tk.X, padx=5, pady=5)
        
        check_new_msg_button = ttk.Button(get_msg_frame, text="检查新消息", command=lambda: self.run_function(self.check_new_message))
        check_new_msg_button.pack(fill=tk.X, padx=5, pady=5)
        
        get_all_msg_button = ttk.Button(get_msg_frame, text="获取当前窗口所有消息", command=lambda: self.run_function(self.get_all_message))
        get_all_msg_button.pack(fill=tk.X, padx=5, pady=5)
        
        get_next_msg_button = ttk.Button(get_msg_frame, text="获取下一个新消息", command=lambda: self.run_function(self.get_next_new_message))
        get_next_msg_button.pack(fill=tk.X, padx=5, pady=5)
        
        get_all_new_msg_button = ttk.Button(get_msg_frame, text="获取所有新消息", command=lambda: self.run_function(self.get_all_new_message))
        get_all_new_msg_button.pack(fill=tk.X, padx=5, pady=5)
        
        load_more_msg_button = ttk.Button(get_msg_frame, text="加载更多历史消息", command=lambda: self.run_function(self.load_more_message))
        load_more_msg_button.pack(fill=tk.X, padx=5, pady=5)
        
        # 聊天监听
        listen_frame = ttk.LabelFrame(parent, text="聊天监听")
        listen_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(listen_frame, text="监听对象:").pack(anchor=tk.W, padx=5, pady=2)
        self.listen_entry = ttk.Entry(listen_frame)
        self.listen_entry.pack(fill=tk.X, padx=5, pady=2)
        
        listen_buttons_frame = ttk.Frame(listen_frame)
        listen_buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        add_listen_button = ttk.Button(listen_buttons_frame, text="添加监听", command=self.add_listen_chat)
        add_listen_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        remove_listen_button = ttk.Button(listen_buttons_frame, text="移除监听", command=self.remove_listen_chat)
        remove_listen_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        get_listen_msg_button = ttk.Button(listen_frame, text="获取监听对象新消息", command=lambda: self.run_function(self.get_listen_message))
        get_listen_msg_button.pack(fill=tk.X, padx=5, pady=5)
        
        get_all_listen_button = ttk.Button(listen_frame, text="获取所有监听对象", command=lambda: self.run_function(self.get_all_listen_chat))
        get_all_listen_button.pack(fill=tk.X, padx=5, pady=5)
    
    def create_contact_tab(self, parent):
        # 获取聊天列表
        session_frame = ttk.LabelFrame(parent, text="聊天列表")
        session_frame.pack(fill=tk.X, padx=5, pady=5)
        
        get_session_list_button = ttk.Button(session_frame, text="获取聊天列表", command=lambda: self.run_function(self.get_session_list))
        get_session_list_button.pack(fill=tk.X, padx=5, pady=5)
        
        get_session_button = ttk.Button(session_frame, text="获取聊天对象详情", command=lambda: self.run_function(self.get_session))
        get_session_button.pack(fill=tk.X, padx=5, pady=5)
        
        get_current_chat_button = ttk.Button(session_frame, text="获取当前聊天对象", command=lambda: self.run_function(self.get_current_chat))
        get_current_chat_button.pack(fill=tk.X, padx=5, pady=5)
        
        # 好友管理
        friend_frame = ttk.LabelFrame(parent, text="好友管理")
        friend_frame.pack(fill=tk.X, padx=5, pady=5)
        
        get_all_friends_button = ttk.Button(friend_frame, text="获取所有好友列表", command=lambda: self.run_function(self.get_all_friends))
        get_all_friends_button.pack(fill=tk.X, padx=5, pady=5)
        
        get_friend_details_button = ttk.Button(friend_frame, text="获取好友详情信息", command=self.get_friend_details)
        get_friend_details_button.pack(fill=tk.X, padx=5, pady=5)
        
        get_group_members_button = ttk.Button(friend_frame, text="获取群成员列表", command=self.get_group_members)
        get_group_members_button.pack(fill=tk.X, padx=5, pady=5)
        
        get_new_friends_button = ttk.Button(friend_frame, text="获取新的好友申请列表", command=lambda: self.run_function(self.get_new_friends))
        get_new_friends_button.pack(fill=tk.X, padx=5, pady=5)
        
        add_new_friend_button = ttk.Button(friend_frame, text="添加新好友", command=self.add_new_friend)
        add_new_friend_button.pack(fill=tk.X, padx=5, pady=5)
    
    def create_file_tab(self, parent):
        # 文件管理
        file_frame = ttk.LabelFrame(parent, text="文件管理")
        file_frame.pack(fill=tk.X, padx=5, pady=5)
        
        download_files_button = ttk.Button(file_frame, text="下载聊天文件", command=self.download_files)
        download_files_button.pack(fill=tk.X, padx=5, pady=5)
    
    # 辅助函数
    def run_function(self, func):
        if not self.is_initialized:
            messagebox.showerror("错误", "请先初始化微信实例")
            return
        
        # 在新线程中运行函数，避免GUI卡顿
        threading.Thread(target=func, daemon=True).start()
    
    def clear_output(self):
        self.output_text.delete(1.0, tk.END)
    
    def log_output(self, message):
        self.output_text.insert(tk.END, f"{message}\n")
        self.output_text.see(tk.END)
    
    # 基本操作函数
    def initialize_wechat(self):
        try:
            language = self.language_var.get()
            debug = self.debug_var.get()
            
            self.log_output(f"正在初始化微信实例 (语言: {language}, 调试模式: {debug})...")
            self.wx = WeChat(language=language, debug=debug)
            self.is_initialized = True
            self.status_var.set(f"状态: 已初始化微信实例 (用户: {self.wx.nickname})")
            self.log_output(f"初始化成功，用户: {self.wx.nickname}")
        except Exception as e:
            self.log_output(f"初始化失败: {str(e)}")
            messagebox.showerror("错误", f"初始化微信实例失败: {str(e)}")
    
    def _show_wechat(self):
        try:
            self.wx._show()
            self.log_output("已显示微信窗口")
        except Exception as e:
            self.log_output(f"显示微信窗口失败: {str(e)}")
    
    def _refresh_wechat(self):
        try:
            self.wx._refresh()
            self.log_output("已刷新微信窗口")
        except Exception as e:
            self.log_output(f"刷新微信窗口失败: {str(e)}")
    
    def _switch_to_chat(self):
        try:
            self.wx.SwitchToChat()
            self.log_output("已切换到聊天页面")
        except Exception as e:
            self.log_output(f"切换到聊天页面失败: {str(e)}")
    
    def _switch_to_contact(self):
        try:
            self.wx.SwitchToContact()
            self.log_output("已切换到通讯录页面")
        except Exception as e:
            self.log_output(f"切换到通讯录页面失败: {str(e)}")
    
    # 聊天功能函数
    def chat_with(self):
        if not self.is_initialized:
            messagebox.showerror("错误", "请先初始化微信实例")
            return
        
        who = self.chat_with_entry.get().strip()
        if not who:
            messagebox.showerror("错误", "请输入聊天对象")
            return
        
        def _chat_with():
            try:
                result = self.wx.ChatWith(who)
                if result:
                    self.log_output(f"已切换到聊天对象: {result}")
                else:
                    self.log_output(f"切换聊天对象失败: {who}")
            except Exception as e:
                self.log_output(f"切换聊天对象失败: {str(e)}")
        
        threading.Thread(target=_chat_with, daemon=True).start()
    
    def send_message(self):
        if not self.is_initialized:
            messagebox.showerror("错误", "请先初始化微信实例")
            return
        
        msg = self.msg_text.get(1.0, tk.END).strip()
        if not msg:
            messagebox.showerror("错误", "请输入消息内容")
            return
        
        who = self.chat_with_entry.get().strip()
        at_text = self.at_entry.get().strip()
        at_list = [name.strip() for name in at_text.split(",")] if at_text else None
        
        def _send_message():
            try:
                self.wx.SendMsg(msg, who=who if who else None, at=at_list)
                self.log_output(f"已发送消息{'给 ' + who if who else ''}")
                self.log_output(f"消息内容: {msg}")
                if at_list:
                    self.log_output(f"@成员: {', '.join(at_list)}")
            except Exception as e:
                self.log_output(f"发送消息失败: {str(e)}")
        
        threading.Thread(target=_send_message, daemon=True).start()
    
    def at_all(self):
        if not self.is_initialized:
            messagebox.showerror("错误", "请先初始化微信实例")
            return
        
        msg = self.msg_text.get(1.0, tk.END).strip()
        who = self.chat_with_entry.get().strip()
        
        def _at_all():
            try:
                self.wx.AtAll(msg=msg if msg else None, who=who if who else None)
                self.log_output(f"已@所有人{'给 ' + who if who else ''}")
                if msg:
                    self.log_output(f"消息内容: {msg}")
            except Exception as e:
                self.log_output(f"@所有人失败: {str(e)}")
        
        threading.Thread(target=_at_all, daemon=True).start()
    
    def browse_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.file_path_var.set(file_path)
    
    def send_file(self):
        if not self.is_initialized:
            messagebox.showerror("错误", "请先初始化微信实例")
            return
        
        file_path = self.file_path_var.get().strip()
        if not file_path:
            messagebox.showerror("错误", "请选择要发送的文件")
            return
        
        who = self.chat_with_entry.get().strip()
        
        def _send_file():
            try:
                result = self.wx.SendFiles(file_path, who=who if who else None)
                if result:
                    self.log_output(f"已发送文件{'给 ' + who if who else ''}")
                    self.log_output(f"文件路径: {file_path}")
                else:
                    self.log_output("发送文件失败")
            except Exception as e:
                self.log_output(f"发送文件失败: {str(e)}")
        
        threading.Thread(target=_send_file, daemon=True).start()
    
    # 消息获取函数
    def check_new_message(self):
        try:
            result = self.wx.CheckNewMessage()
            self.log_output(f"是否有新消息: {result}")
        except Exception as e:
            self.log_output(f"检查新消息失败: {str(e)}")
    
    def get_all_message(self):
        try:
            messages = self.wx.GetAllMessage()
            self.log_output(f"获取到 {len(messages)} 条消息:")
            for i, msg in enumerate(messages):
                self.log_output(f"[{i+1}] {msg}")
        except Exception as e:
            self.log_output(f"获取所有消息失败: {str(e)}")
    
    def get_next_new_message(self):
        try:
            messages = self.wx.GetNextNewMessage()
            if messages:
                self.log_output("获取到新消息:")
                for session, msgs in messages.items():
                    self.log_output(f"聊天对象: {session}")
                    for i, msg in enumerate(msgs):
                        self.log_output(f"[{i+1}] {msg}")
            else:
                self.log_output("没有新消息")
        except Exception as e:
            self.log_output(f"获取下一个新消息失败: {str(e)}")
    
    def get_all_new_message(self):
        try:
            messages = self.wx.GetAllNewMessage()
            if messages:
                self.log_output("获取到所有新消息:")
                for session, msgs in messages.items():
                    self.log_output(f"聊天对象: {session}")
                    for i, msg in enumerate(msgs):
                        self.log_output(f"[{i+1}] {msg}")
            else:
                self.log_output("没有新消息")
        except Exception as e:
            self.log_output(f"获取所有新消息失败: {str(e)}")
    
    def load_more_message(self):
        try:
            self.wx.LoadMoreMessage()
            self.log_output("已加载更多历史消息")
        except Exception as e:
            self.log_output(f"加载更多历史消息失败: {str(e)}")
    
    # 聊天监听函数
    def add_listen_chat(self):
        if not self.is_initialized:
            messagebox.showerror("错误", "请先初始化微信实例")
            return
        
        who = self.listen_entry.get().strip()
        if not who:
            messagebox.showerror("错误", "请输入监听对象")
            return
        
        def _add_listen_chat():
            try:
                self.wx.AddListenChat(who)
                self.log_output(f"已添加监听对象: {who}")
            except Exception as e:
                self.log_output(f"添加监听对象失败: {str(e)}")
        
        threading.Thread(target=_add_listen_chat, daemon=True).start()
    
    def remove_listen_chat(self):
        if not self.is_initialized:
            messagebox.showerror("错误", "请先初始化微信实例")
            return
        
        who = self.listen_entry.get().strip()
        if not who:
            messagebox.showerror("错误", "请输入监听对象")
            return
        
        def _remove_listen_chat():
            try:
                self.wx.RemoveListenChat(who)
                self.log_output(f"已移除监听对象: {who}")
            except Exception as e:
                self.log_output(f"移除监听对象失败: {str(e)}")
        
        threading.Thread(target=_remove_listen_chat, daemon=True).start()
    
    def get_listen_message(self):
        try:
            messages = self.wx.GetListenMessage()
            if messages:
                self.log_output("获取到监听对象新消息:")
                for session, msgs in messages.items():
                    self.log_output(f"聊天对象: {session}")
                    for i, msg in enumerate(msgs):
                        self.log_output(f"[{i+1}] {msg}")
            else:
                self.log_output("没有监听对象新消息")
        except Exception as e:
            self.log_output(f"获取监听对象新消息失败: {str(e)}")
    
    def get_all_listen_chat(self):
        try:
            listen_chats = self.wx.GetAllListenChat()
            self.log_output(f"获取到 {len(listen_chats)} 个监听对象:")
            for i, chat in enumerate(listen_chats):
                self.log_output(f"[{i+1}] {chat}")
        except Exception as e:
            self.log_output(f"获取所有监听对象失败: {str(e)}")
    
    # 联系人管理函数
    def get_session_list(self):
        try:
            session_list = self.wx.GetSessionList()
            self.log_output(f"获取到 {len(session_list)} 个聊天对象:")
            for i, (name, amount) in enumerate(session_list.items()):
                self.log_output(f"[{i+1}] {name} {'(有 ' + str(amount) + ' 条新消息)' if amount > 0 else ''}")
        except Exception as e:
            self.log_output(f"获取聊天列表失败: {str(e)}")
    
    def get_session(self):
        try:
            sessions = self.wx.GetSession()
            self.log_output(f"获取到 {len(sessions)} 个聊天对象详情:")
            for i, session in enumerate(sessions):
                self.log_output(f"[{i+1}] 名称: {session.name}")
                self.log_output(f"    时间: {session.time}")
                self.log_output(f"    内容: {session.content}")
                self.log_output(f"    是否有新消息: {session.isnew}")
        except Exception as e:
            self.log_output(f"获取聊天对象详情失败: {str(e)}")
    
    def get_current_chat(self):
        try:
            current_chat = self.wx.CurrentChat()
            self.log_output(f"当前聊天对象: {current_chat}")
        except Exception as e:
            self.log_output(f"获取当前聊天对象失败: {str(e)}")
    
    def get_all_friends(self):
        try:
            friends = self.wx.GetAllFriends()
            self.log_output(f"获取到 {len(friends)} 个好友:")
            for i, friend in enumerate(friends):
                self.log_output(f"[{i+1}] {friend}")
        except Exception as e:
            self.log_output(f"获取所有好友列表失败: {str(e)}")
    
    def get_friend_details(self):
        if not self.is_initialized:
            messagebox.showerror("错误", "请先初始化微信实例")
            return
        
        # 弹出对话框获取获取好友数量
        n = simpledialog.askinteger("获取好友详情", "请输入要获取的好友数量 (0表示获取所有):", initialvalue=10, minvalue=0)
        if n is None:
            return
        
        def _get_friend_details():
            try:
                self.log_output(f"正在获取好友详情信息 (数量: {'所有' if n == 0 else n})...")
                details = self.wx.GetFriendDetails(n if n > 0 else None)
                self.log_output(f"获取到 {len(details)} 个好友详情:")
                for i, detail in enumerate(details):
                    self.log_output(f"[{i+1}] 好友详情:")
                    for key, value in detail.items():
                        self.log_output(f"    {key}: {value}")
            except Exception as e:
                self.log_output(f"获取好友详情信息失败: {str(e)}")
        
        threading.Thread(target=_get_friend_details, daemon=True).start()
    
    def get_group_members(self):
        if not self.is_initialized:
            messagebox.showerror("错误", "请先初始化微信实例")
            return
        
        group_name = simpledialog.askstring("获取群成员列表", "请输入群聊名称:")
        if not group_name:
            return
        
        def _get_group_members():
            try:
                self.log_output(f"正在获取群 '{group_name}' 的成员列表...")
                members = self.wx.GetGroupMembers(group_name)
                self.log_output(f"获取到 {len(members)} 个群成员:")
                for i, member in enumerate(members):
                    self.log_output(f"[{i+1}] {member}")
            except Exception as e:
                self.log_output(f"获取群成员列表失败: {str(e)}")
        
        threading.Thread(target=_get_group_members, daemon=True).start()
    
    def get_new_friends(self):
        try:
            new_friends = self.wx.GetNewFriends()
            self.log_output(f"获取到 {len(new_friends)} 个新的好友申请:")
            for i, friend in enumerate(new_friends):
                self.log_output(f"[{i+1}] {friend}")
        except Exception as e:
            self.log_output(f"获取新的好友申请列表失败: {str(e)}")
    
    def add_new_friend(self):
        if not self.is_initialized:
            messagebox.showerror("错误", "请先初始化微信实例")
            return
        
        # 弹出对话框获取好友信息
        add_window = tk.Toplevel(self.root)
        add_window.title("添加新好友")
        add_window.geometry("300x200")
        add_window.resizable(False, False)
        
        ttk.Label(add_window, text="搜索内容:").pack(anchor=tk.W, padx=10, pady=5)
        search_entry = ttk.Entry(add_window, width=30)
        search_entry.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(add_window, text="验证消息:").pack(anchor=tk.W, padx=10, pady=5)
        verify_entry = ttk.Entry(add_window, width=30)
        verify_entry.pack(fill=tk.X, padx=10, pady=5)
        
        def _add_friend():
            search_content = search_entry.get().strip()
            verify_msg = verify_entry.get().strip()
            
            if not search_content:
                messagebox.showerror("错误", "请输入搜索内容")
                return
            
            add_window.destroy()
            
            def _add_new_friend_thread():
                try:
                    self.log_output(f"正在添加好友 '{search_content}'...")
                    result = self.wx.AddNewFriend(search_content, verify_msg)
                    if result:
                        self.log_output(f"已成功发送好友申请: {search_content}")
                    else:
                        self.log_output(f"发送好友申请失败: {search_content}")
                except Exception as e:
                    self.log_output(f"添加新好友失败: {str(e)}")
            
            threading.Thread(target=_add_new_friend_thread, daemon=True).start()
        
        button_frame = ttk.Frame(add_window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="取消", command=add_window.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="添加", command=_add_friend).pack(side=tk.RIGHT, padx=5)
    
    # 文件管理函数
    def download_files(self):
        if not self.is_initialized:
            messagebox.showerror("错误", "请先初始化微信实例")
            return
        
        # 弹出对话框获取下载信息
        download_window = tk.Toplevel(self.root)
        download_window.title("下载聊天文件")
        download_window.geometry("400x200")
        download_window.resizable(False, False)
        
        ttk.Label(download_window, text="聊天对象:").pack(anchor=tk.W, padx=10, pady=5)
        who_entry = ttk.Entry(download_window, width=30)
        who_entry.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(download_window, text="保存路径:").pack(anchor=tk.W, padx=10, pady=5)
        path_frame = ttk.Frame(download_window)
        path_frame.pack(fill=tk.X, padx=10, pady=5)
        
        path_var = tk.StringVar()
        path_entry = ttk.Entry(path_frame, textvariable=path_var, width=30)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        def browse_dir():
            dir_path = filedialog.askdirectory()
            if dir_path:
                path_var.set(dir_path)
        
        browse_button = ttk.Button(path_frame, text="浏览", command=browse_dir)
        browse_button.pack(side=tk.RIGHT, padx=5)
        
        def _download_files():
            who = who_entry.get().strip()
            save_path = path_var.get().strip()
            
            if not who:
                messagebox.showerror("错误", "请输入聊天对象")
                return
            
            if not save_path:
                messagebox.showerror("错误", "请选择保存路径")
                return
            
            download_window.destroy()
            
            def _download_files_thread():
                try:
                    self.log_output(f"正在下载 '{who}' 的聊天文件到 '{save_path}'...")
                    from wxauto import WeChatFiles
                    wf = WeChatFiles(self.wx)
                    files = wf.DownloadFiles(who, save_path)
                    self.log_output(f"已下载 {len(files)} 个文件:")
                    for i, file in enumerate(files):
                        self.log_output(f"[{i+1}] {file}")
                except Exception as e:
                    self.log_output(f"下载聊天文件失败: {str(e)}")
            
            threading.Thread(target=_download_files_thread, daemon=True).start()
        
        button_frame = ttk.Frame(download_window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="取消", command=download_window.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="下载", command=_download_files).pack(side=tk.RIGHT, padx=5)


# 主程序入口
if __name__ == "__main__":
    root = tk.Tk()
    app = WeChatTestApp(root)
    root.mainloop()