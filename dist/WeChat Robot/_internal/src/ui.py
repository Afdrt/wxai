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
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', 'assets', 'config.png')))
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('配置')
        self.setMinimumWidth(600)
        layout = QVBoxLayout(self)
        
        # 创建选项卡界面
        tab_widget = QTabWidget()
        tab_widget.setDocumentMode(True)  # 更现代的选项卡外观
        
        # 基础配置选项卡
        basic_tab = QWidget()
        basic_layout = QVBoxLayout(basic_tab)
        
        # AI基础配置
        ai_group = QGroupBox('API配置')
        ai_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        ai_layout = QFormLayout()
        ai_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setText(self.config.get('api_key', ''))
        show_hide_btn = QPushButton()
        show_hide_btn.setIcon(QIcon.fromTheme("eye"))
        show_hide_btn.setFixedWidth(30)
        show_hide_btn.setToolTip("显示/隐藏API Key")
        show_hide_btn.clicked.connect(self.toggle_api_key_visibility)
        
        api_key_layout = QHBoxLayout()
        api_key_layout.addWidget(self.api_key_input)
        api_key_layout.addWidget(show_hide_btn)
        
        ai_layout.addRow('API Key:', api_key_layout)
        
        self.api_base_input = QLineEdit()
        self.api_base_input.setPlaceholderText('默认使用OpenAI官方地址')
        self.api_base_input.setText(self.config.get('service', ''))
        ai_layout.addRow('服务地址:', self.api_base_input)
        
        self.model_input = QComboBox()
        self.model_input.setEditable(True)
        self.model_input.addItems(['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo', 'gpt-3.5-turbo-16k'])
        self.model_input.setCurrentText(self.config.get('model', ''))
        ai_layout.addRow('模型名称:', self.model_input)
        
        ai_group.setLayout(ai_layout)
        basic_layout.addWidget(ai_group)
        
        # AI行为配置
        behavior_group = QGroupBox('AI行为配置')
        behavior_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        behavior_layout = QVBoxLayout()
        
        prompt_label = QLabel('系统提示词:')
        self.system_prompt_input = QTextEdit()
        self.system_prompt_input.setPlaceholderText('设置AI助手的行为和角色')
        self.system_prompt_input.setText(self.config.get('ai_behavior', {}).get('system_prompt', 
            "你是一个友好的AI助手，请用简洁自然的方式回复用户的问题。"))
        self.system_prompt_input.setMinimumHeight(120)
        
        # 添加提示词模板选择
        template_layout = QHBoxLayout()
        template_label = QLabel("快速模板:")
        self.template_combo = QComboBox()
        self.template_combo.addItems([
            "选择模板...",
            "友好助手",
            "专业顾问",
            "简洁回答",
            "幽默风格"
        ])
        self.template_combo.currentIndexChanged.connect(self.apply_template)
        template_layout.addWidget(template_label)
        template_layout.addWidget(self.template_combo)
        template_layout.addStretch()
        
        behavior_layout.addLayout(template_layout)
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
        params_info.setStyleSheet("QGroupBox { font-weight: bold; }")
        params_info_layout = QVBoxLayout()
        info_text = QLabel(
            "• 创造性: 值越高，回复越有创意但可能偏离主题\n"
            "• 最大长度: 控制AI回复的最大字符数\n"
            "• 多样性: 值越高，回复越多样化\n"
            "• 重复惩罚: 值越高，AI越不会重复之前说过的内容\n"
            "• 话题新鲜度: 值越高，AI越倾向于引入新话题"
        )
        info_text.setWordWrap(True)
        info_text.setStyleSheet("color: #555; background-color: #f8f8f8; padding: 10px; border-radius: 5px;")
        params_info_layout.addWidget(info_text)
        params_info.setLayout(params_info_layout)
        advanced_layout.addWidget(params_info)
        
        # AI参数调整
        params_group = QGroupBox('模型参数调整')
        params_group.setStyleSheet("QGroupBox { font-weight: bold; }")
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
        
        # 添加重置按钮
        reset_btn = QPushButton("重置为默认值")
        reset_btn.clicked.connect(self.reset_parameters)
        params_layout.addWidget(reset_btn, 5, 0, 1, 3, Qt.AlignCenter)
        
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
        
        # 应用样式
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QGroupBox {
                border: 1px solid #cccccc;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
            }
            QPushButton {
                background-color: #4a86e8;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #3a76d8;
            }
            QPushButton:pressed {
                background-color: #2a66c8;
            }
            QLineEdit, QTextEdit, QComboBox {
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 3px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: #cccccc;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #4a86e8;
                border: 1px solid #5c5c5c;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }
        """)
    
    def toggle_api_key_visibility(self):
        """切换API Key的可见性"""
        if self.api_key_input.echoMode() == QLineEdit.Password:
            self.api_key_input.setEchoMode(QLineEdit.Normal)
        else:
            self.api_key_input.setEchoMode(QLineEdit.Password)
    
    def apply_template(self, index):
        """应用提示词模板"""
        if index == 0:  # "选择模板..."
            return
        
        templates = {
            1: "你是一个友好的AI助手，请用简洁自然的方式回复用户的问题。尽量提供有帮助的信息，并保持礼貌和耐心。",
            2: "你是一个专业的顾问，提供准确、深入的分析和建议。回答应该基于事实和专业知识，避免主观判断。",
            3: "你是一个注重效率的助手，请直接回答问题要点，避免冗长的解释和不必要的客套话。",
            4: "你是一个幽默风趣的AI助手，在回答问题的同时适当加入一些轻松的幽默元素，让交流更加愉快。"
        }
        
        if index in templates:
            self.system_prompt_input.setText(templates[index])
        
        # 重置下拉框到"选择模板..."
        self.template_combo.setCurrentIndex(0)
    
    def reset_parameters(self):
        """重置参数为默认值"""
        default_values = {
            'temperature': 0.7,
            'max_tokens': 800,
            'presence_penalty': 0.0,
            'frequency_penalty': 0.0,
            'top_p': 1.0
        }
        
        self.temperature_input.setValue(default_values['temperature'])
        self.max_tokens_input.setValue(default_values['max_tokens'])
        self.presence_penalty_input.setValue(default_values['presence_penalty'])
        self.frequency_penalty_input.setValue(default_values['frequency_penalty'])
        self.top_p_input.setValue(default_values['top_p'])
        
        QMessageBox.information(self, "重置完成", "已将所有参数重置为默认值")

    def get_config(self) -> Dict:
        """获取当前配置"""
        return {
            'api_key': self.api_key_input.text(),
            'service': self.api_base_input.text().strip(),
            'model': self.model_input.currentText().strip(),
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
            new_config = self.get_config()
            
            # 验证API Key
            if not new_config['api_key'].strip():
                QMessageBox.warning(self, '配置错误', 'API Key 不能为空，请输入有效的 API Key。')
                self.api_key_input.setFocus()
                return
            
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
        
        # 尝试加载图标
        icon_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'icon.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            
        self.init_ui()
        
        # 设置样式表
        self.apply_stylesheet()
    
    def init_ui(self) -> None:
        """初始化UI界面"""
        self.setWindowTitle(self.config.get('window_title', '微信AI助手'))
        self.resize(*self.config.get('window_size', (900, 650)))
        
        # 设置窗口始终在最上层
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        
        # 创建中心部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # 创建水平分割的布局
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)
        
        # 左侧面板 - 监听列表
        left_panel = QGroupBox('监听列表')
        left_panel.setStyleSheet("QGroupBox { font-weight: bold; }")
        left_layout = QVBoxLayout()
        
        # 搜索框
        search_layout = QHBoxLayout()
        search_icon = QLabel()
        search_icon.setPixmap(QIcon.fromTheme("search").pixmap(16, 16))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索监听目标...")
        self.search_input.textChanged.connect(self.filter_targets)
        search_layout.addWidget(search_icon)
        search_layout.addWidget(self.search_input)
        left_layout.addLayout(search_layout)
        
        # 监听目标列表
        self.target_list = QListWidget()
        self.target_list.setAlternatingRowColors(True)
        self.target_list.setSelectionMode(QAbstractItemView.ExtendedSelection)  # 允许多选
        left_layout.addWidget(self.target_list)
        
        # 监听列表按钮
        button_layout = QHBoxLayout()
        self.add_button = QPushButton('添加')
        self.add_button.setIcon(QIcon.fromTheme("list-add"))
        self.remove_button = QPushButton('移除')
        self.remove_button.setIcon(QIcon.fromTheme("list-remove"))
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        left_layout.addLayout(button_layout)
        
        # 添加监听操作按钮
        listen_button_layout = QHBoxLayout()
        self.listen_button = QPushButton('监听选中')
        self.listen_button.setIcon(QIcon.fromTheme("media-record"))
        self.unlisten_button = QPushButton('取消监听')
        self.unlisten_button.setIcon(QIcon.fromTheme("media-playback-stop"))
        listen_button_layout.addWidget(self.listen_button)
        listen_button_layout.addWidget(self.unlisten_button)
        left_layout.addLayout(listen_button_layout)
        
        left_panel.setLayout(left_layout)
        
        # 右侧面板 - 日志显示
        right_panel = QGroupBox('日志')
        right_panel.setStyleSheet("QGroupBox { font-weight: bold; }")
        right_layout = QVBoxLayout()
        
        # 添加工具栏
        log_toolbar = QHBoxLayout()
        
        # 清空日志按钮
        self.clear_log_button = QPushButton("清空日志")
        self.clear_log_button.setIcon(QIcon.fromTheme("edit-clear"))
        self.clear_log_button.clicked.connect(self.clear_logs)
        
        # 保存日志按钮
        self.save_log_button = QPushButton("保存日志")
        self.save_log_button.setIcon(QIcon.fromTheme("document-save"))
        self.save_log_button.clicked.connect(self.save_logs)
        
        log_toolbar.addWidget(self.clear_log_button)
        log_toolbar.addWidget(self.save_log_button)
        log_toolbar.addStretch()
        
        right_layout.addLayout(log_toolbar)
        
        self.message_display = QTextEdit()
        self.message_display.setReadOnly(True)
        self.message_display.setStyleSheet("""
            QTextEdit {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 5px;
                font-family: 'Microsoft YaHei', Arial, sans-serif;
            }
        """)
        right_layout.addWidget(self.message_display)
        
        right_panel.setLayout(right_layout)
        
        # 添加左右面板到水平布局
        content_layout.addWidget(left_panel, 1)
        content_layout.addWidget(right_panel, 2)
        
        # 添加水平布局到主布局
        main_layout.addLayout(content_layout)
        
        # 底部控制面板
        control_panel = QHBoxLayout()
        
        # 状态指示器
        self.status_indicator = QLabel("状态: 未运行")
        self.status_indicator.setStyleSheet("color: #888888; font-weight: bold;")
        control_panel.addWidget(self.status_indicator)
        
        # 在控制面板中添加自动回复开关
        self.auto_reply_checkbox = QCheckBox('启用AI自动回复')
        self.auto_reply_checkbox.setChecked(True)  # 默认开启
        self.auto_reply_checkbox.setStyleSheet("QCheckBox { font-weight: bold; }")
        control_panel.addWidget(self.auto_reply_checkbox)
        
        control_panel.addStretch()
        
        # 控制按钮
        self.start_button = QPushButton('开始监听')
        self.start_button.setIcon(QIcon.fromTheme("media-playback-start"))
        self.stop_button = QPushButton('停止监听')
        self.stop_button.setIcon(QIcon.fromTheme("media-playback-stop"))
        self.config_button = QPushButton('配置')
        self.config_button.setIcon(QIcon.fromTheme("preferences-system"))
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
        
        # 创建状态栏
        self.statusBar().showMessage('准备就绪')
    
    def apply_stylesheet(self):
        """应用全局样式表"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                border: 1px solid #cccccc;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
            }
            QPushButton {
                background-color: #4a86e8;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #3a76d8;
            }
            QPushButton:pressed {
                background-color: #2a66c8;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #888888;
            }
            QLineEdit, QTextEdit {
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 3px;
            }
            QListWidget {
                border: 1px solid #cccccc;
                border-radius: 3px;
                alternate-background-color: #f0f0f0;
            }
            QListWidget::item:selected {
                background-color: #4a86e8;
                color: white;
            }
            QCheckBox {
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 15px;
                height: 15px;
            }
            QCheckBox::indicator:unchecked {
                border: 1px solid #cccccc;
                background-color: white;
                border-radius: 2px;
            }
            QCheckBox::indicator:checked {
                border: 1px solid #4a86e8;
                background-color: #4a86e8;
                border-radius: 2px;
            }
        """)
    
    def filter_targets(self, text):
        """根据搜索文本过滤目标列表"""
        for i in range(self.target_list.count()):
            item = self.target_list.item(i)
            if text.lower() in item.text().lower():
                item.setHidden(False)
            else:
                item.setHidden(True)
    
    def clear_logs(self):
        """清空日志显示"""
        reply = QMessageBox.question(self, '确认', '确定要清空所有日志吗？',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.message_display.clear()
            self.update_status("日志已清空")
    
    def save_logs(self):
        """保存日志到文件"""
        file_path, _ = QFileDialog.getSaveFileName(self, "保存日志", "", "文本文件 (*.txt);;所有文件 (*)")
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.message_display.toPlainText())
                self.update_status(f"日志已保存到: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存日志失败: {str(e)}")
    
    def update_status(self, status: str) -> None:
        """更新状态显示"""
        self.message_display.append(f"[系统] {status}")
        self.status_indicator.setText(f"状态: {status}")
        self.statusBar().showMessage(status, 3000)  # 在状态栏显示3秒
    
    def add_message(self, sender: str, message: Dict[str, str]) -> None:
        """添加新消息到显示区域"""
        msg_html = f"""<p>
            <b>{sender}</b> ({message['time']})<br/>
            <span style='color: {'blue' if message['type'] != '处理错误' else 'red'};'>
                [{message['type']}] {message['content']}
            </span>
        </p>"""
        self.message_display.append(msg_html)
        # 自动滚动到底部
        self.message_display.verticalScrollBar().setValue(
            self.message_display.verticalScrollBar().maximum()
        )
    
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
            # 检查是否已存在
            exists = False
            for i in range(self.target_list.count()):
                if self.target_list.item(i).text() == target:
                    exists = True
                    break
            
            if exists:
                QMessageBox.warning(self, '警告', f'监听目标 "{target}" 已存在')
                return
                
            self.target_list.addItem(target)
            # 添加后保存配置
            self.save_targets_config()
            self.update_status(f'已添加监听目标: {target}')

    def remove_target(self) -> None:
        """移除监听目标"""
        selected_items = self.target_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, '警告', '请先选择要移除的监听目标')
            return
        
        reply = QMessageBox.question(self, '确认', f'确定要移除选中的 {len(selected_items)} 个监听目标吗？',
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
            
        # 从列表中移除所有选中项
        for item in selected_items:
            target = item.text()
            self.target_list.takeItem(self.target_list.row(item))
            self.update_status(f'已移除监听目标: {target}')
            
        # 保存更新后的配置
        self.save_targets_config()

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
            QMessageBox.critical(self, "错误", f"保存监听目标配置失败: {str(e)}")
    
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
            self.update_status(f"读取配置文件失败: {str(e)}")
            return {}
    
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
            self.update_status("配置已保存")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存配置文件错误: {e}")
    
    def set_running_state(self, is_running: bool) -> None:
        """设置运行状态"""
        self.start_button.setEnabled(not is_running)  # 运行时禁用开始按钮
        self.stop_button.setEnabled(is_running)  # 只有运行时启用停止按钮
        
        if is_running:
            self.status_indicator.setText("状态: 正在运行")
            self.status_indicator.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.status_indicator.setText("状态: 已停止")
            self.status_indicator.setStyleSheet("color: #888888; font-weight: bold;")
    
    def show_config_dialog(self):
        """显示配置对话框"""
        dialog = ConfigDialog(self.config, self)
        if dialog.exec_() == QDialog.Accepted:
            self.config.update(dialog.get_config())
            self.save_config(self.config)
            self.update_status("配置已更新")
            
            # 检查配置完整性
            if not self.config.get('api_key'):
                self.update_status("警告: API Key 未设置，请在开始监听前完成配置")
    
    def is_auto_reply_enabled(self) -> bool:
        """获取自动回复开关状态"""
        return self.auto_reply_checkbox.isChecked()
    
    def set_buttons_enabled(self, enabled):
        """设置开始/停止按钮的启用状态"""
        self.start_button.setEnabled(enabled)
        self.stop_button.setEnabled(enabled)

    def listen_selected_target(self):
        """监听选中的目标"""
        selected_items = self.target_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, '警告', '请先选择要监听的目标')
            return
        
        success_count = 0
        for item in selected_items:
            target = item.text()
            # 调用主程序的方法添加监听
            if hasattr(self, 'add_listener_handler') and self.add_listener_handler:
                try:
                    self.add_listener_handler(target)
                    success_count += 1
                except Exception as e:
                    self.update_status(f"监听 {target} 失败: {str(e)}")
            else:
                self.update_status(f"无法添加监听: {target}，功能未初始化")
        
        if success_count > 0:
            self.update_status(f"已成功添加 {success_count} 个监听目标")
    
    def unlisten_selected_target(self):
        """取消监听选中的目标"""
        selected_items = self.target_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, '警告', '请先选择要取消监听的目标')
            return
        
        success_count = 0
        for item in selected_items:
            target = item.text()
            # 调用主程序的方法取消监听
            if hasattr(self, 'remove_listener_handler') and self.remove_listener_handler:
                try:
                    self.remove_listener_handler(target)
                    success_count += 1
                except Exception as e:
                    self.update_status(f"取消监听 {target} 失败: {str(e)}")
            else:
                self.update_status(f"无法取消监听: {target}，功能未初始化")
        
        if success_count > 0:
            self.update_status(f"已成功取消 {success_count} 个监听目标")

    # 添加设置处理器的方法
    def set_add_listener_handler(self, handler):
        """设置添加监听处理器"""
        self.add_listener_handler = handler

    def set_remove_listener_handler(self, handler):
        """设置取消监听处理器"""
        self.remove_listener_handler = handler