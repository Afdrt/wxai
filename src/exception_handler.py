import sys
import traceback
import logging
from PyQt5.QtWidgets import QMessageBox

class GlobalExceptionHandler:
    """全局异常处理器，用于捕获未处理的异常并记录到日志"""
    
    def __init__(self, logger=None):
        """初始化异常处理器
        
        Args:
            logger: 日志记录器，如果为None则使用根日志记录器
        """
        self.logger = logger or logging.getLogger()
        self.original_hook = sys.excepthook
        
    def install(self):
        """安装全局异常处理器"""
        sys.excepthook = self.handle_exception
        self.logger.info("全局异常处理器已安装")
        
    def uninstall(self):
        """卸载全局异常处理器"""
        sys.excepthook = self.original_hook
        self.logger.info("全局异常处理器已卸载")
        
    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """处理未捕获的异常
        
        Args:
            exc_type: 异常类型
            exc_value: 异常值
            exc_traceback: 异常堆栈
        """
        # 获取异常的详细信息
        exception_info = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        
        # 记录异常到日志
        self.logger.critical(f"未捕获的异常: {exc_value}", exc_info=(exc_type, exc_value, exc_traceback))
        
        # 显示错误对话框（如果在GUI环境中）
        try:
            QMessageBox.critical(
                None, 
                "程序错误", 
                f"程序遇到了一个未处理的错误:\n\n{exc_value}\n\n详细信息已记录到日志文件。"
            )
        except Exception:
            # 如果无法显示GUI对话框，则打印到控制台
            print(f"严重错误: {exc_value}\n{exception_info}", file=sys.stderr)
        
        # 调用原始的异常处理器
        self.original_hook(exc_type, exc_value, exc_traceback)

def setup_thread_exception_hook():
    """设置线程异常钩子，捕获QThread中的异常"""
    import threading
    
    original_thread_run = threading.Thread.run
    
    def patched_thread_run(*args, **kwargs):
        try:
            original_thread_run(*args, **kwargs)
        except Exception as e:
            sys.excepthook(type(e), e, e.__traceback__)
    
    threading.Thread.run = patched_thread_run