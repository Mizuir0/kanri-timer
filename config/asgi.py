"""
ASGI config for band rehearsal timer project.
WebSocket + HTTP 対応
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

# Django ASGI アプリケーション初期化
django_asgi_app = get_asgi_application()

# WebSocket URL routing
from apps.timer_core.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    # HTTP リクエスト処理
    "http": django_asgi_app,
    
    # WebSocket リクエスト処理
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})