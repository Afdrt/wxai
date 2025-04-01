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
    
    def accept(self):
        """当用户点击确定时保存配置"""
        try:
            # 获取UI中的值
            new_config = {
                'api_key': self.api_key_input.text(),
                'service': self.api_base_input.text().strip(),
                'model': self.model_input.text().strip(),
                'listen_targets': self.config.get('listen_targets', [])  # 保持原有的监听目标
            }
            
            # 保存到文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(new_config, f, indent=4, ensure_ascii=False)
            
            super().accept()
        except Exception as e:
            QMessageBox.critical(self, '错误', f'保存配置失败: {str(e)}')
    
    def init_ui(self):
        self.setWindowTitle('配置')
        layout = QVBoxLayout(self)
        
        # AI配置
        ai_group = QGroupBox('AI配置')
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
        layout.addWidget(ai_group)
        
        # 按钮
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_config(self) -> Dict:
        return {
            'api_key': self.api_key_input.text(),
            'service': self.api_base_input.text().strip(),
            'model': self.model_input.text().strip()
        }

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
    
    def remove_target(self) -> None:
        """移除监听目标"""
        current_item = self.target_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, '警告', '请先选择要移除的监听目标')
            return
            
        target = current_item.text()
        # 从配置中移除
        if target in self.config.get('listen_targets', []):
            self.config['listen_targets'].remove(target)
            # 保存配置
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            # 从列表中移除
            self.target_list.takeItem(self.target_list.row(current_item))
            self.update_status(f'已移除监听目标: {target}')
    
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
        self.stop_button.setEnabled(True)  # 停止按钮始终可用
        self.config_button.setEnabled(not is_running)  # 运行时禁用配置按钮
        self.add_button.setEnabled(not is_running)  # 运行时禁用添加按钮
        self.remove_button.setEnabled(not is_running)  # 运行时禁用移除按钮
    
    
    def show_config_dialog(self):
        """显示配置对话框"""
        dialog = ConfigDialog(self.config, self)
        if dialog.exec_() == QDialog.Accepted:
            self.config.update(dialog.get_config())
            self.save_config(self.config)

    def is_auto_reply_enabled(self) -> bool:
            """获取自动回复开关状态"""
            return self.auto_reply_checkbox.isChecked()