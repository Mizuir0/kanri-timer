from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
import json
import uuid
from .models import Band, Timer
from .tasks import countdown_timer, get_timer_status

def timer_main(request):
    """メインタイマー画面"""
    # 全ての有効なタイマーを取得
    timers = Timer.objects.filter(is_active=True).select_related('band').order_by('band__name', 'order')
    
    return render(request, 'timer_core/timer_main.html', {
        'timers': timers
    })

@csrf_exempt
def start_timer(request):
    """タイマー開始API"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            timer_id = data.get('timer_id')
            
            # タイマー情報取得
            timer = Timer.objects.get(id=timer_id)
            total_seconds = timer.duration_minutes * 60
            
            # セッションID生成
            session_id = str(uuid.uuid4())
            
            # Celeryタスクでタイマー開始
            countdown_timer.delay(session_id, total_seconds)
            
            return JsonResponse({
                'success': True,
                'session_id': session_id,
                'message': f'{timer.band.name}のタイマーを開始しました',
                'duration': timer.duration_minutes
            })
            
        except Timer.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'タイマーが見つかりません'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'POSTメソッドが必要です'})

def timer_status(request, session_id):
    """タイマー状態取得API"""
    try:
        status = get_timer_status.delay(session_id).get()
        return JsonResponse({
            'success': True,
            'status': status
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })