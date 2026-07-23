from .models import SystemSetting


def system_settings(request):
    return {
        "system_settings": SystemSetting.get_settings()
    }