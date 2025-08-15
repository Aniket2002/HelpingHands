import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mindbridge.settings.development')

# For now, just use HTTP. We'll add WebSocket support later when channels is installed
application = get_asgi_application()
