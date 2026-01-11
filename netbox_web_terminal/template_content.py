try:
    from netbox.plugins import PluginTemplateExtension
except ImportError:
    from extras.plugins import PluginTemplateExtension

class DeviceTerminalButton(PluginTemplateExtension):
    model = 'dcim.device'

    def buttons(self):
        obj = self.context.get('object') or self.context.get('record')
        
        if not obj:
            return ""
            
        # 检查是否有管理 IP
        ip_obj = getattr(obj, 'primary_ip4', None) or getattr(obj, 'primary_ip6', None)
        
        if ip_obj:
            return self.render('netbox_web_terminal/inc/terminal_button.html', {
                'device': obj,
            })
        return ""

template_extensions = [DeviceTerminalButton]
