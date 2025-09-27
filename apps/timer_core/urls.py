from django.urls import path
from . import views

app_name = 'timer_core'

urlpatterns = [
    path('', views.band_list, name='band_list'),           # バンド一覧（トップページ）
    path('band/<int:band_id>/', views.timer_list, name='timer_list'),  # タイマー一覧
]