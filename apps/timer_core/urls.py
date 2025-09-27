from django.urls import path
from . import views

app_name = 'timer_core'

urlpatterns = [
    path('', views.timer_main, name='timer_main'),
]