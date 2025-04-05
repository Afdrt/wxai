from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import json
import os
from typing import Dict, List, Optional, Callable

class ConfigDialog(QDialog):
    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self.config = config.copy()  # 创建配置的副本
        self.config_file = os.path.join(os.path.dirname(__file__), '..', 'config.json')
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('配置')
        layout = QVBoxLayout(self)
        
        # 创建选项卡界面
        tab_widget = QTabWidget()
        
        # 基础配置选项卡
        basic_tab = QWidget()
        basic_layout = QVBoxLayout(basic_tab)
        
        # AI基础配置
        ai_group = QGroupBox('API配置')
        ai_layout = QFormLayout()
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setText(self.config.get('api_key', ''))
        ai_layout.addRow('API Key:', self.api_key_input)
        
        self.api_base_input = QLineEdit()
        self.api_base_input.setPlaceholderText('默认使用OpenAI官方地址')
        self.api_base_input.setText(self.config.get('service', ''))
        ai_layout.addRow('服务地址:', self.api_base_input)
        
        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText('请输入模型名称')
        self.model_input.setText(self.config.get('model', ''))
        ai_layout.addRow('模型名称:', self.model_input)
        
        ai_group.setLayout(ai_layout)
        basic_layout.addWidget(ai_group)
        
        # AI行为配置
        behavior_group = QGroupBox('AI行为配置')
        behavior_layout = QVBoxLayout()
        
        prompt_label = QLabel('系统提示词:')
        self.system_prompt_input = QTextEdit()
        self.system_prompt_input.setPlaceholderText('设置AI助手的行为和角色')
        self.system_prompt_input.setText(self.config.get('ai_behavior', {}).get('system_prompt', 
            "你是一个友好的AI助手，请用简洁自然的方式回复用户的问题。"))
        self.system_prompt_input.setMinimumHeight(100)
        
        behavior_layout.addWidget(prompt_label)
        behavior_layout.addWidget(self.system_prompt_input)
        behavior_group.setLayout(behavior_layout)
        basic_layout.addWidget(behavior_group)
        
        # 添加基础配置选项卡
        tab_widget.addTab(basic_tab, "基础配置")
        
        # 高级参数选项卡
        advanced_tab = QWidget()
        advanced_layout = QVBoxLayout(advanced_tab)
        
        # 参数说明
        params_info = QGroupBox('参数说明')
        params_info_layout = QVBoxLayout()
        info_text = QLabel(
            "• 创造性: 值越高，回复越有创意但可能偏离主题\n"
            "• 最大长度: 控制AI回复的最大字符数\n"
            "• 多样性: 值越高，回复越多样化\n"
            "• 重复惩罚: 值越高，AI越不会重复之前说过的内容\n"
            "• 话题新鲜度: 值越高，AI越倾向于引入新话题"
        )
        info_text.setWordWrap(True)
        params_info_layout.addWidget(info_text)
        params_info.setLayout(params_info_layout)
        advanced_layout.addWidget(params_info)
        
        # AI参数调整
        params_group = QGroupBox('模型参数调整')
        params_layout = QGridLayout()
        
        # 创造性
        temp_label = QLabel('创造性 (0-1):')
        self.temperature_input = QDoubleSpinBox()
        self.temperature_input.setRange(0.0, 1.0)
        self.temperature_input.setSingleStep(0.01)
        self.temperature_input.setValue(self.config.get('ai_behavior', {}).get('temperature', 0.7))
        self.temperature_slider = QSlider(Qt.Horizontal)
        self.temperature_slider.setRange(0, 100)
        self.temperature_slider.setValue(int(self.temperature_input.value() * 100))
        self.temperature_slider.valueChanged.connect(lambda v: self.temperature_input.setValue(v/100))
        self.temperature_input.valueChanged.connect(lambda v: self.temperature_slider.setValue(int(v*100)))
        
        # 最大长度
        max_tokens_label = QLabel('最大长度 (0-2000):')
        self.max_tokens_input = QSpinBox()
        self.max_tokens_input.setRange(0, 2000)
        self.max_tokens_input.setSingleStep(100)
        self.max_tokens_input.setValue(self.config.get('ai_behavior', {}).get('max_tokens', 800))
        self.max_tokens_slider = QSlider(Qt.Horizontal)
        self.max_tokens_slider.setRange(0, 2000)
        self.max_tokens_slider.setValue(self.max_tokens_input.value())
        self.max_tokens_slider.valueChanged.connect(self.max_tokens_input.setValue)
        self.max_tokens_input.valueChanged.connect(self.max_tokens_slider.setValue)
        
        # 多样性
        presence_label = QLabel('多样性 (0-1):')
        self.presence_penalty_input = QDoubleSpinBox()
        self.presence_penalty_input.setRange(0.0, 1.0)
        self.presence_penalty_input.setSingleStep(0.01)
        self.presence_penalty_input.setValue(self.config.get('ai_behavior', {}).get('presence_penalty', 0.9))
        self.presence_slider = QSlider(Qt.Horizontal)
        self.presence_slider.setRange(0, 100)
        self.presence_slider.setValue(int(self.presence_penalty_input.value() * 100))
        self.presence_slider.valueChanged.connect(lambda v: self.presence_penalty_input.setValue(v/100))
        self.presence_penalty_input.valueChanged.connect(lambda v: self.presence_slider.setValue(int(v*100)))
        
        # 重复惩罚
        freq_label = QLabel('重复惩罚 (0-1):')
        self.frequency_penalty_input = QDoubleSpinBox()
        self.frequency_penalty_input.setRange(0.0, 1.0)
        self.frequency_penalty_input.setSingleStep(0.01)
        self.frequency_penalty_input.setValue(self.config.get('ai_behavior', {}).get('frequency_penalty', 0.0))
        self.frequency_slider = QSlider(Qt.Horizontal)
        self.frequency_slider.setRange(0, 100)
        self.frequency_slider.setValue(int(self.frequency_penalty_input.value() * 100))
        self.frequency_slider.valueChanged.connect(lambda v: self.frequency_penalty_input.setValue(v/100))
        self.frequency_penalty_input.valueChanged.connect(lambda v: self.frequency_slider.setValue(int(v*100)))
        
        # 话题新鲜度
        top_p_label = QLabel('话题新鲜度 (0-1):')
        self.top_p_input = QDoubleSpinBox()
        self.top_p_input.setRange(0.0, 1.0)
        self.top_p_input.setSingleStep(0.01)
        self.top_p_input.setValue(self.config.get('ai_behavior', {}).get('top_p', 0.0))
        self.top_p_slider = QSlider(Qt.Horizontal)
        self.top_p_slider.setRange(0, 100)
        self.top_p_slider.setValue(int(self.top_p_input.value() * 100))
        self.top_p_slider.valueChanged.connect(lambda v: self.top_p_input.setValue(v/100))
        self.top_p_input.valueChanged.connect(lambda v: self.top_p_slider.setValue(int(v*100)))
        
        # 添加到网格布局
        params_layout.addWidget(temp_label, 0, 0)
        params_layout.addWidget(self.temperature_input, 0, 1)
        params_layout.addWidget(self.temperature_slider, 0, 2)
        
        params_layout.addWidget(max_tokens_label, 1, 0)
        params_layout.addWidget(self.max_tokens_input, 1, 1)
        params_layout.addWidget(self.max_tokens_slider, 1, 2)
        
        params_layout.addWidget(presence_label, 2, 0)
        params_layout.addWidget(self.presence_penalty_input, 2, 1)
        params_layout.addWidget(self.presence_slider, 2, 2)
        
        params_layout.addWidget(freq_label, 3, 0)
        params_layout.addWidget(self.frequency_penalty_input, 3, 1)
        params_layout.addWidget(self.frequency_slider, 3, 2)
        
        params_layout.addWidget(top_p_label, 4, 0)
        params_layout.addWidget(self.top_p_input, 4, 1)
        params_layout.addWidget(self.top_p_slider, 4, 2)
        
        params_group.setLayout(params_layout)
        advanced_layout.addWidget(params_group)
        
        # 添加高级参数选项卡
        tab_widget.addTab(advanced_tab, "高级参数")
        
        # 添加选项卡到主布局
        layout.addWidget(tab_widget)
        
        # 按钮
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_config(self) -> Dict:
        """获取当前配置"""
        return {
            'api_key': self.api_key_input.text(),
            'service': self.api_base_input.text().strip(),
            'model': self.model_input.text().strip(),
            'listen_targets': self.config.get('listen_targets', []),
            'ai_behavior': {
                'system_prompt': self.system_prompt_input.toPlainText().strip(),
                'temperature': self.temperature_input.value(),
                'max_tokens': self.max_tokens_input.value(),
                'presence_penalty': self.presence_penalty_input.value(),
                'frequency_penalty': self.frequency_penalty_input.value(),
                'top_p': self.top_p_input.value()
            }
        }

    def accept(self):
        """当用户点击确定时保存配置"""
        try:
            # 获取UI中的值
            new_config = {
                'api_key': self.api_key_input.text(),
                'service': self.api_base_input.text().strip(),
                'model': self.model_input.text().strip(),
                'listen_targets': self.config.get('listen_targets', []),
                'ai_behavior': {
                    'system_prompt': self.system_prompt_input.toPlainText().strip(),
                    'temperature': self.temperature_input.value(),
                    'max_tokens': self.max_tokens_input.value(),
                    'presence_penalty': self.presence_penalty_input.value(),
                    'frequency_penalty': self.frequency_penalty_input.value(),
                    'top_p': self.top_p_input.value()
                }
            }
            
            # 保存到文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(new_config, f, indent=4, ensure_ascii=False)
            
            super().accept()
        except Exception as e:
            QMessageBox.critical(self, '错误', f'保存配置失败: {str(e)}')

class ChatWindow(QMainWindow):
    def __init__(self, config: dict):
        super().__init__()
        self.config = config
        self.config_file = os.path.join(os.path.dirname(__file__), '..', 'config.json')
        self.load_config()
        self.init_ui()
    
    def init_ui(self) -> None:
        """初始化UI界面"""
        self.setWindowTitle(self.config.get('window_title', '微信AI助手'))
        self.resize(*self.config.get('window_size', (800, 600)))
        
        # 设置窗口始终在最上层
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        
        # 创建中心部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 创建水平分割的布局
        content_layout = QHBoxLayout()
        
        # 左侧面板 - 监听列表
        left_panel = QGroupBox('监听列表')
        left_layout = QVBoxLayout()
        
        # 监听目标列表
        self.target_list = QListWidget()
        left_layout.addWidget(self.target_list)
        
        # 监听列表按钮
        button_layout = QHBoxLayout()
        self.add_button = QPushButton('添加')
        self.remove_button = QPushButton('移除')
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        left_layout.addLayout(button_layout)
        
        # 添加监听操作按钮
        listen_button_layout = QHBoxLayout()
        self.listen_button = QPushButton('监听选中')
        self.unlisten_button = QPushButton('取消监听')
        listen_button_layout.addWidget(self.listen_button)
        listen_button_layout.addWidget(self.unlisten_button)
        left_layout.addLayout(listen_button_layout)
        
        left_panel.setLayout(left_layout)
        
        # 右侧面板 - 日志显示
        right_panel = QGroupBox('日志')
        right_layout = QVBoxLayout()
        
        self.message_display = QTextEdit()
        self.message_display.setReadOnly(True)
        right_layout.addWidget(self.message_display)
        
        right_panel.setLayout(right_layout)
        
        # 添加左右面板到水平布局
        content_layout.addWidget(left_panel, 1)
        content_layout.addWidget(right_panel, 2)
        
        # 添加水平布局到主布局
        main_layout.addLayout(content_layout)
        
        # 底部控制面板
        # 在控制面板中添加自动回复开关
        control_panel = QHBoxLayout()
        
        self.auto_reply_checkbox = QCheckBox('启用AI自动回复')
        self.auto_reply_checkbox.setChecked(True)  # 默认开启
        control_panel.addWidget(self.auto_reply_checkbox)
        
        # 控制按钮
        self.start_button = QPushButton('开始监听')
        self.stop_button = QPushButton('停止监听')
        self.config_button = QPushButton('配置')
        self.stop_button.setEnabled(False)
        
        control_panel.addWidget(self.start_button)
        control_panel.addWidget(self.stop_button)
        control_panel.addWidget(self.config_button)
        
        main_layout.addLayout(control_panel)
        
        # 连接信号
        self.add_button.clicked.connect(self.add_target)
        self.remove_button.clicked.connect(self.remove_target)
        self.config_button.clicked.connect(self.show_config_dialog)
        self.listen_button.clicked.connect(self.listen_selected_target)
        self.unlisten_button.clicked.connect(self.unlisten_selected_target)
        
        # 加载已有监听目标
        self.load_targets()
    
    def update_status(self, status: str) -> None:
        """更新状态显示"""
        self.message_display.append(f"[系统] {status}")
    
    def add_message(self, sender: str, message: Dict[str, str]) -> None:
        """添加新消息到显示区域"""
        msg_html = f"""<p>
            <b>{sender}</b> ({message['time']})<br/>
            <span style='color: {'blue' if message['type'] != '处理错误' else 'red'};'>
                [{message['type']}] {message['content']}
            </span>
        </p>"""
        self.message_display.append(msg_html)
    
    def set_start_handler(self, handler: Callable[[], None]) -> None:
        """设置开始按钮的处理函数"""
        self.start_button.clicked.connect(handler)
    
    def set_stop_handler(self, handler: Callable[[], None]) -> None:
        """设置停止按钮的处理函数"""
        self.stop_button.clicked.connect(handler)
    
    def add_target(self):
        """添加监听目标"""
        target, ok = QInputDialog.getText(self, '添加监听目标', '请输入监听目标名称:')
        if ok and target:
            self.target_list.addItem(target)
            # 添加后保存配置
            self.save_targets_config()

    def remove_target(self) -> None:
        """移除监听目标"""
        current_item = self.target_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, '警告', '请先选择要移除的监听目标')
            return
            
        target = current_item.text()
        # 从列表中移除
        self.target_list.takeItem(self.target_list.row(current_item))
        # 保存更新后的配置
        self.save_targets_config()
        self.update_status(f'已移除监听目标: {target}')

    def save_targets_config(self):
        """保存监听目标到配置文件"""
        try:
            # 读取现有配置
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 更新监听目标
            config['listen_targets'] = [
                self.target_list.item(i).text()
                for i in range(self.target_list.count())
            ]
            
            # 保存配置
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"保存监听目标配置失败: {str(e)}")
    
    def get_config(self) -> Dict:
        """获取当前配置"""
        try:
            # 从配置文件读取基础配置
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 更新监听目标列表
            config['listen_targets'] = [
                self.target_list.item(i).text()
                for i in range(self.target_list.count())
            ]
            return config
            
        except Exception as e:
            print(f"读取配置文件失败: {str(e)}")
            return {}
        config = self.config.copy()
        config['listen_targets'] = [
            self.target_list.item(i).text()
            for i in range(self.target_list.count())
        ]
        return config
    
    def load_targets(self):
        """加载监听目标"""
        targets = self.config.get('listen_targets', [])
        self.target_list.clear()
        self.target_list.addItems(targets)
    
    def load_config(self) -> None:
        """从配置文件加载配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
        except Exception as e:
            print(f"加载配置文件错误: {e}")
            
    def save_config(self, config: Dict) -> None:
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存配置文件错误: {e}")
    
    def set_running_state(self, is_running: bool) -> None:
        """设置运行状态"""
        self.start_button.setEnabled(not is_running)  # 运行时禁用开始按钮
        self.stop_button.setEnabled(is_running)  # 只有运行时启用停止按钮
    
    def show_config_dialog(self):
        """显示配置对话框"""
        dialog = ConfigDialog(self.config, self)
        if dialog.exec_() == QDialog.Accepted:
            self.config.update(dialog.get_config())
            self.save_config(self.config)
    def is_auto_reply_enabled(self) -> bool:
            """获取自动回复开关状态"""
            return self.auto_reply_checkbox.isChecked()
    def set_buttons_enabled(self, enabled):
        """设置开始/停止按钮的启用状态"""
        self.start_button.setEnabled(enabled)
        self.stop_button.setEnabled(enabled)

    def listen_selected_target(self):
        """监听选中的目标"""
        current_item = self.target_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, '警告', '请先选择要监听的目标')
            return
            
        target = current_item.text()
        # 调用主程序的方法添加监听
        if hasattr(self, 'add_listener_handler') and self.add_listener_handler:
            self.add_listener_handler(target)
        else:
            self.update_status(f"无法添加监听: {target}，功能未初始化")
    
    def unlisten_selected_target(self):
        """取消监听选中的目标"""
        current_item = self.target_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, '警告', '请先选择要取消监听的目标')
            return
            
        target = current_item.text()
        # 调用主程序的方法取消监听
        if hasattr(self, 'remove_listener_handler') and self.remove_listener_handler:
            self.remove_listener_handler(target)
        else:
            self.update_status(f"无法取消监听: {target}，功能未初始化")

    # 添加设置处理器的方法
    def set_add_listener_handler(self, handler):
        """设置添加监听处理器"""
        self.add_listener_handler = handler

    def set_remove_listener_handler(self, handler):
        """设置取消监听处理器"""
        self.remove_listener_handler = handler