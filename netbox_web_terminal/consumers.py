import json
import threading
import paramiko
from channels.generic.websocket import WebsocketConsumer
from dcim.models import Device
from django.conf import settings

class TerminalConsumer(WebsocketConsumer):
    def connect(self):
        self.device_id = self.scope['url_route']['kwargs']['pk']
        self.user = self.scope['user']
        
        if not self.user.is_authenticated:
            self.close()
            return

        try:
            self.device = Device.objects.get(pk=self.device_id)
            self.accept()
            
            # 获取连接参数
            ip_obj = self.device.primary_ip4 or self.device.primary_ip6
            if not ip_obj:
                self.send_message("错误: 设备没有管理 IP\r\n")
                self.close()
                return

            self.host = str(ip_obj.address.ip)
            
            # 1. 获取插件默认配置
            plugin_config = settings.PLUGINS_CONFIG.get('netbox_web_terminal', {})
            default_username = plugin_config.get('ssh_username', 'admin')
            default_password = plugin_config.get('ssh_password', '')

            # 2. 从 WebSocket 查询参数中获取用户输入的凭据
            from urllib.parse import parse_qs
            query_params = parse_qs(self.scope['query_string'].decode())
            
            # 如果用户在弹窗中输入了内容，则使用输入值；否则使用默认值
            user_input_name = query_params.get('username', [None])[0]
            user_input_pass = query_params.get('password', [None])[0]

            self.username = user_input_name if user_input_name else default_username
            self.password = user_input_pass if user_input_pass else default_password

            # 3. 获取终端初始大小
            try:
                self.rows = int(query_params.get('rows', [24])[0])
                self.cols = int(query_params.get('cols', [80])[0])
            except (ValueError, TypeError):
                self.rows = 24
                self.cols = 80

            # 启动 SSH 线程
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            try:
                self.ssh_client.connect(
                    hostname=self.host,
                    username=self.username,
                    password=self.password,
                    look_for_keys=False,
                    timeout=10
                )
                self.channel = self.ssh_client.invoke_shell(
                    term='xterm', 
                    width=self.cols, 
                    height=self.rows
                )
                
                # 开启监听线程
                self.thread = threading.Thread(target=self.receive_ssh)
                self.thread.daemon = True
                self.thread.start()
                
            except Exception as e:
                self.send_message(f"SSH 连接失败: {str(e)}\r\n")
                self.close()

        except Device.DoesNotExist:
            self.close()

    def disconnect(self, close_code):
        if hasattr(self, 'ssh_client'):
            self.ssh_client.close()

    def receive(self, text_data):
        data = json.loads(text_data)
        if 'data' in data:
            self.channel.send(data['data'])
        elif 'resize' in data:
            rows = data['resize'].get('rows')
            cols = data['resize'].get('cols')
            if rows and cols:
                self.channel.resize_pty(width=cols, height=rows)

    def receive_ssh(self):
        try:
            while True:
                # 阻塞式读取，更高效
                data = self.channel.recv(4096)
                if not data:
                    break
                # 解码并发送
                self.send_message(data.decode('utf-8', errors='ignore'))
        except Exception:
            pass
        finally:
            self.close()

    def send_message(self, message):
        # 尝试发送二进制数据，这对于处理复杂的终端转义序列和编码更稳健
        if isinstance(message, str):
            try:
                # 优先以二进制形式发送原始数据
                self.send(bytes_data=message.encode('utf-8'))
            except Exception:
                # 回退到 JSON 包装的文本（用于错误提示等）
                self.send(text_data=json.dumps({
                    'message': message
                }))
        else:
            # message 已经是 bytes
            self.send(bytes_data=message)
