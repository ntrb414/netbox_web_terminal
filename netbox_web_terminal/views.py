from django.shortcuts import render
from django.views.generic import View
from dcim.models import Device
from django.contrib.auth.mixins import PermissionRequiredMixin

class DeviceTerminalView(PermissionRequiredMixin, View):
    permission_required = 'dcim.view_device'

    def get(self, request, pk):
        device = Device.objects.get(pk=pk)
        ip_obj = device.primary_ip4 or device.primary_ip6
        
        if not ip_obj:
            return render(request, 'netbox_web_terminal/terminal.html', {
                'device': device,
                'error': "设备没有管理IP"
            })

        ip = str(ip_obj.address.ip)
        
        # 获取表单提交的用户名和密码
        ssh_username = request.GET.get('ssh_username', '').strip()
        ssh_password = request.GET.get('ssh_password', '').strip()
        
        return render(request, 'netbox_web_terminal/terminal.html', {
            'device': device,
            'device_ip': ip,
            'ssh_username': ssh_username,
            'ssh_password': ssh_password,
        })
