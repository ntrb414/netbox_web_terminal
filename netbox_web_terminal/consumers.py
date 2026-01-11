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
            
            # 从插件配置获取默认凭据 (生产环境建议使用加密存储或动态输入)
            plugin_config = settings.PLUGINS_CONFIG.get('netbox_web_terminal', {})
            self.username = plugin_config.get('ssh_username', 'admin')
            self.password = plugin_config.get('ssh_password', '')

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
                self.channel = self.ssh_client.invoke_shell(term='xterm', width=80, height=24)
                
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

    def receive_ssh(self):
        while True:
            if self.channel.recv_ready():
                data = self.channel.recv(1024).decode('utf-8', errors='ignore')
                self.send_message(data)
            if self.channel.exit_status_ready():
                break

    def send_message(self, message):
        self.send(text_data=json.dumps({
            'message': message
        }))
