from wxauto import *
import time
import datetime

# 获取当前微信客户端
wx = WeChat()
print(f"微信客户端初始化成功，当前登录账号：{wx.nickname}")

# 指定要监听的聊天对象列表，为空则监听所有对象
# 例如: ["张三", "工作群", "家人群"]
listen_targets = ['微信支付','文件传输助手']
if listen_targets:
    print(f"已设置指定监听对象: {', '.join(listen_targets)}")
    
    # 为每个监听对象添加监听
    for target in listen_targets:
        try:
            wx.AddListenChat(target, savepic=True, savefile=True, savevoice=True)
            print(f"成功添加监听对象: {target}")
        except Exception as e:
            print(f"添加监听对象 {target} 失败: {str(e)}")
else:
    print("当前监听所有聊天对象")

# 记录开始监听的时间
start_time = time.time()
print(f"开始监听新消息: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
print("请在其他设备上向当前微信账号发送消息...")
print("-" * 50)

# 初始化消息ID记录，避免重复接收
last_msg_ids = {}

# 持续监听新消息
try:
    while True:
        # 如果有指定监听对象，使用GetListenMessage方法获取消息
        if listen_targets:
            for target in listen_targets:
                new_messages = wx.GetListenMessage(target)
                
                if new_messages:
                    current_time = time.time()
                    elapsed_time = current_time - start_time
                    
                    print(f"\n接收到来自 {target} 的新消息:")
                    print(f"接收时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
                    print(f"监听延迟: {elapsed_time:.3f} 秒")
                    
                    for msg in new_messages:
                        # 安全地处理不同类型的消息对象
                        try:
                            # 检查是否为SysMessage类型
                            if hasattr(msg, '__class__') and msg.__class__.__name__ == 'SysMessage':
                                # 系统消息特殊处理
                                msg_type = "系统消息"
                                msg_content = str(msg)
                                msg_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                msg_id = "系统消息ID"
                            else:
                                # 普通消息处理
                                msg_type = msg[0] if isinstance(msg, (list, tuple)) and len(msg) > 0 else "未知类型"
                                msg_content = msg[1] if isinstance(msg, (list, tuple)) and len(msg) > 1 else str(msg)
                                msg_time = msg[2] if isinstance(msg, (list, tuple)) and len(msg) > 2 else datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                msg_id = msg[-1] if isinstance(msg, (list, tuple)) and len(msg) > 3 else "未知ID"
                        except Exception as e:
                            # 如果处理过程中出现任何错误，使用安全的默认值
                            msg_type = "处理错误"
                            msg_content = f"消息处理错误: {str(e)}, 原始消息: {str(msg)}"
                            msg_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            msg_id = "错误ID"
                            
                        print(f"消息类型: {msg_type}")
                        print(f"消息内容: {msg_content}")
                        print(f"消息时间: {msg_time}")
                        print(f"消息ID: {msg_id}")
                    
                    # 向发送消息的联系人自动回复"你好"
                    try:
                        wx.SendMsg("你好", who=target)
                        print(f"已向 {target} 自动回复: 你好")
                    except Exception as e:
                        print(f"向 {target} 发送自动回复失败: {str(e)}")
                    
                    print("-" * 50)
                    
                    # 更新开始时间为当前时间
                    start_time = current_time
        else:
            # 如果没有指定监听对象，使用原来的方法获取所有新消息
            if wx.CheckNewMessage():
                new_msg = wx.GetNextNewMessage(savepic=True, savefile=True, savevoice=True)
                
                if new_msg:
                    current_time = time.time()
                    elapsed_time = current_time - start_time
                    
                    # 打印接收到的消息信息
                    for chat_name, messages in new_msg.items():
                        # 检查是否为新消息，避免重复处理
                        msg_ids = []
                        for msg in messages:
                            if isinstance(msg, (list, tuple)) and len(msg) > 3:
                                msg_ids.append(msg[-1])
                        
                        # 过滤出真正的新消息
                        new_messages = []
                        for msg in messages:
                            # 安全地处理不同类型的消息
                            if isinstance(msg, (list, tuple)) and len(msg) > 3:
                                msg_id = msg[-1]
                                if chat_name not in last_msg_ids or msg_id not in last_msg_ids[chat_name]:
                                    new_messages.append(msg)
                                    # 更新已处理消息ID
                                    if chat_name not in last_msg_ids:
                                        last_msg_ids[chat_name] = []
                                    last_msg_ids[chat_name].append(msg_id)
                            else:
                                # 对于不符合预期格式的消息，直接添加到新消息列表
                                new_messages.append(msg)
                        
                        if new_messages:
                            print(f"\n接收到来自 {chat_name} 的新消息:")
                            print(f"接收时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
                            print(f"监听延迟: {elapsed_time:.3f} 秒")
                            
                            for msg in new_messages:
                                try:
                                    # 检查是否为SysMessage类型
                                    if hasattr(msg, '__class__') and msg.__class__.__name__ == 'SysMessage':
                                        # 系统消息特殊处理
                                        msg_type = "系统消息"
                                        msg_content = str(msg)
                                        msg_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                        msg_id = "系统消息ID"
                                    else:
                                        # 普通消息处理
                                        msg_type = msg[0] if isinstance(msg, (list, tuple)) and len(msg) > 0 else "未知类型"
                                        msg_content = msg[1] if isinstance(msg, (list, tuple)) and len(msg) > 1 else str(msg)
                                        msg_time = msg[2] if isinstance(msg, (list, tuple)) and len(msg) > 2 else datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                        msg_id = msg[-1] if isinstance(msg, (list, tuple)) and len(msg) > 3 else "未知ID"
                                except Exception as e:
                                    # 如果处理过程中出现任何错误，使用安全的默认值
                                    msg_type = "处理错误"
                                    msg_content = f"消息处理错误: {str(e)}, 原始消息: {str(msg)}"
                                    msg_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                    msg_id = "错误ID"
                                
                                print(f"消息类型: {msg_type}")
                                print(f"消息内容: {msg_content}")
                                print(f"消息时间: {msg_time}")
                                print(f"消息ID: {msg_id}")
                            
                            print("-" * 50)
                    
                    # 更新开始时间为当前时间
                    start_time = current_time
        
        # 短暂休眠，避免CPU占用过高，但保持足够短以确保不会漏掉消息
        time.sleep(0.01)
        
except KeyboardInterrupt:
    print("\n监听已停止")
    total_time = time.time() - start_time
    print(f"总监听时间: {total_time:.3f} 秒")
    
    # 移除所有监听对象
    if listen_targets:
        for target in listen_targets:
            try:
                wx.RemoveListenChat(target)
                print(f"已移除监听对象: {target}")
            except Exception as e:
                print(f"移除监听对象 {target} 失败: {str(e)}")

# 获取好友信息
friends = wx.GetAllFriends()  # 修正方法名：GetFriends -> GetAllFriends
for friend in friends:
    print(f"好友昵称: {friend['NickName']}, 备注: {friend['RemarkName']}")

# 获取群组信息
groups = wx.GetAllChatrooms()  # 修正方法名：GetGroups -> GetAllChatrooms
for group in groups:
    print(f"群组名称: {group['NickName']}, 成员数量: {group['MemberCount']}")