from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import json
import os
from typing import Dict, List, Optional, Callable

class ChatWindow(QMainWindow):
    def __init__(self, config: dict):
        super().__init__()
        self.config = config
        self.config_file = os.path.join(os.path.dirname(__file__), '..', 'config.json')
        self.load_config()
        self.init_ui()
        
    def init_ui(self) -> None:
        """初始化UI界面"""
        # 设置窗口属性
        self.setWindowTitle(self.config.get('window_title', '微信AI助手'))
        self.resize(*self.config.get('window_size', (800, 600)))
        

        
        # 创建中心部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 创建状态显示区域
        self.status_label = QLabel('未连接')
        layout.addWidget(self.status_label)
        
        # 创建消息显示区域
        self.message_display = QTextEdit()
        self.message_display.setReadOnly(True)
        layout.addWidget(self.message_display)
        
        # 创建配置区域
        config_group = QGroupBox('配置')
        config_layout = QFormLayout()
        
        # AI配置
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        config_layout.addRow('API Key:', self.api_key_input)
        
        self.api_base_input = QLineEdit()
        self.api_base_input.setPlaceholderText('默认使用OpenAI官方地址')
        config_layout.addRow('服务地址:', self.api_base_input)
        
        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText('请输入模型名称')
        config_layout.addRow('模型名称:', self.model_input)
        
        # 监听目标配置
        self.target_input = QLineEdit()
        config_layout.addRow('监听目标:', self.target_input)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # 设置默认配置值
        self.api_key_input.setText(self.config.get('api_key', ''))
        self.api_base_input.setText(self.config.get('service', ''))
        self.model_input.setText(self.config.get('model', ''))
        self.target_input.setText(', '.join(self.config.get('listen_targets', [])))
        
        # 创建控制按钮
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton('开始监听')
        self.stop_button = QPushButton('停止监听')
        self.stop_button.setEnabled(False)
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        layout.addLayout(button_layout)
        
        # 设置状态栏
        self.statusBar().showMessage('就绪')
    
    def update_status(self, status: str) -> None:
        """更新状态显示"""
        self.status_label.setText(status)
        self.statusBar().showMessage(status)
    
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
    
    def get_config(self) -> Dict:
        """获取当前配置"""
        config = {
            'api_key': self.api_key_input.text(),
            'listen_targets': [t.strip() for t in self.target_input.text().split(',') if t.strip()],
            'service': self.api_base_input.text().strip() or self.config.get('service', ''),
            'model': self.model_input.text().strip() or self.config.get('model', '')
        }
        
        self.save_config(config)
        return config
        
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
        self.start_button.setEnabled(not is_running)
        self.stop_button.setEnabled(is_running)
        self.api_key_input.setEnabled(not is_running)
        self.target_input.setEnabled(not is_running)
        self.model_input.setEnabled(not is_running)