# NetBox Web Terminal 插件

NetBox Web Terminal 是一款专为 NetBox 设计的插件，允许网络工程师直接通过 NetBox 设备详情页面，在浏览器中通过 SSH 协议安全地访问网络设备。

## 功能特性

- **一键访问**：在设备详情页集成终端按钮，点击即连。
- **自适应布局**：基于 xterm.js，完美支持窗口缩放和字符对齐。
- **实时同步**：支持终端尺寸自适应（Resize），确保远程会话与浏览器窗口同步。
- **历史回溯**：支持滚动条查看历史输出。
- **自动滚动**：智能识别用户行为，实现输出自动滚动。

## 环境要求

- **NetBox**: 3.0+
- **Python**: 3.8+
- **Django Channels**: 用于 WebSocket 通信
- **Redis**: 作为 Channels 的后端存储
- **Paramiko**: 负责底层的 SSH 连接

## 部署方案

### 1. 放置插件代码
将 `netbox_web_terminal` 目录放置在您的 NetBox 插件存放路径下（通常是 `NetDevOps-sourcecode/source_code/`）。

### 2. 安装依赖
进入插件目录，执行以下命令安装必要依赖：
```bash
pip install paramiko channels
```
或者使用 `setup.py` 安装：
```bash
pip install -e .
```

### 3. 配置 NetBox
修改 NetBox 的配置文件 `configuration.py`（通常位于 `/opt/netbox/netbox/netbox/configuration.py`）：

```python
# 添加插件到已启用列表
PLUGINS = [
    'netbox_web_terminal',
]

# (可选) 配置插件默认参数
PLUGINS_CONFIG = {
    'netbox_web_terminal': {
        'ssh_username': 'admin',  # 默认 SSH 用户名
        'ssh_password': '',       # 默认密码
    }
}
```

### 4. 配置 ASGI
确保 NetBox 使用 ASGI 运行以支持 WebSocket。在 `netbox/asgi.py` 中，需要包含插件的路由：

```python
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import netbox_web_terminal.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'netbox.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            netbox_web_terminal.routing.websocket_urlpatterns
        )
    ),
})
```

### 5. 重启服务
完成配置后，重启 NetBox 相关服务：
```bash
sudo systemctl restart netbox netbox-rq
```

## 使用说明
1. 进入任意设备的详情页面。
2. 在右上角或按钮组中找到 **Terminal** 按钮。
3. 点击后将弹出终端窗口，输入凭据即可开始操作。

## 技术支持
如有疑问或建议，请访问 GitHub 仓库：[ntrb414/netbox_web_terminal](https://github.com/ntrb414/netbox_web_terminal.git)
