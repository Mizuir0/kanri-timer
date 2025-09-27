from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('timer/', include('apps.timer_core.urls')),
]
