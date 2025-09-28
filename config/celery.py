# config/celery.py
import os
from celery import Celery

# Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

# Create Celery app
app = Celery('kanri_timer')

# Configure Celery with Redis - explicit transport
app.conf.update(
    # Broker settings with explicit Redis transport
    broker_url='redis://redis:6379/1',
    broker_transport='redis',
    broker_transport_options={'visibility_timeout': 3600},
    broker_connection_retry_on_startup=True,
    
    # Result backend settings
    result_backend='redis://redis:6379/2',
    result_backend_transport_options={'visibility_timeout': 3600},
    result_expires=3600,
    
    # Task settings
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    task_always_eager=False,
    task_eager_propagates=True,
    
    # Timezone settings
    timezone='Asia/Tokyo',
    enable_utc=True,
    
    # Worker settings
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)

# Load task modules from all registered Django apps
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')