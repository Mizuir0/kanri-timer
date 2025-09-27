from django.shortcuts import render, get_object_or_404
from .models import Band, Timer

def timer_main(request):
    """メインタイマー画面"""
    timers = Timer.objects.filter(is_active=True).select_related('band').order_by('order')

    return render(request, 'timer_core/timer_main.html', {
        'timers': timers
    })
