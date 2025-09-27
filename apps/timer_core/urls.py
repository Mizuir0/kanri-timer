from django.urls import path
from . import views

app_name = 'timer_core'

urlpatterns = [
    path('', views.timer_main, name='timer_main'),         # タイマーメイン画面（トップページ）
    path('api/start-timer/', views.start_timer, name='start_timer'),    # タイマー開始API
    path('api/timer-status/<str:session_id>/', views.timer_status, name='timer_status'),  # タイマー状態API
]