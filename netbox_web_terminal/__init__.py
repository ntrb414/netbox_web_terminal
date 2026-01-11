try:
    from netbox.plugins import PluginConfig
except ImportError:
    from extras.plugins import PluginConfig

class WebTerminalConfig(PluginConfig):
    name = 'netbox_web_terminal'
    verbose_name = 'Web SSH 终端'
    description = '在设备页面提供 Web SSH 终端功能'
    version = '0.1'
    base_url = 'web-terminal'
    default_settings = {
        'ssh_username': 'admin',
        'ssh_password': '',
    }

config = WebTerminalConfig
