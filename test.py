from wxauto import *
import time
import datetime

# 要监听的用户列表
listen_users = ['文件传输助手','小武子','微信支付']

def main():
    # 初始化微信实例
    wx = WeChat()
    print("开始监听消息...")
    
    # 为每个用户添加监听
    for user in listen_users:
        wx.AddListenChat(user)
        print(f"已添加监听用户: {user}")
    
    # 持续监听消息
    try:
        while True:
            # 获取所有监听用户的新消息
            messages = wx.GetListenMessage()
            
            # 如果有新消息
            if messages:
                for chat_window, msgs in messages.items():
                    for msg in msgs:
                        # 打印消息信息
                        print(f"\n时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                        print(f"发送者: {chat_window.name}")  # 直接使用chat_window的name属性
                        print(f"消息内容: {msg}")
            
            # 休眠1秒，避免占用过多CPU
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n停止监听...")
    except Exception as e:
        print(f"\n发生错误: {e}")

if __name__ == "__main__":
    main()