from django.urls import path
from . import views

app_name = 'timer_core'

urlpatterns = [
    path('', views.timer_main, name='timer_main'),         # タイマーメイン画面（トップページ）
    
    # タイマー制御API
    path('api/start-timer/', views.start_timer, name='start_timer'),           # タイマー開始API
    path('api/timer-status/<str:session_id>/', views.timer_status, name='timer_status'),  # タイマー状態API
    path('api/pause-timer/<str:session_id>/', views.pause_timer, name='pause_timer'),    # タイマー一時停止API
    path('api/resume-timer/<str:session_id>/', views.resume_timer, name='resume_timer'),  # タイマー再開API
    
    # テスト用エンドポイント
    path('api/test-celery/', views.test_celery_connection, name='test_celery'),  # Celery接続テスト
]