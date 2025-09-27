from django.shortcuts import render, get_object_or_404
from .models import Band, Timer

def band_list(request):
    """バンド一覧画面"""
    bands = Band.objects.all()
    return render(request, 'timer_core/band_list.html', {
        'bands': bands
    })

def timer_list(request, band_id):
    """タイマー一覧画面"""
    band = get_object_or_404(Band, id=band_id)
    timers = Timer.objects.filter(band=band, is_active=True).order_by('order')
    
    return render(request, 'timer_core/timer_list.html', {
        'band': band,
        'timers': timers
    })