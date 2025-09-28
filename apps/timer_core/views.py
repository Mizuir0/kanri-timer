from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
import json
import uuid
import logging
from .models import Band, Timer
from .tasks import start_timer_session, get_timer_status, pause_timer_session, resume_timer_session, test_celery

logger = logging.getLogger(__name__)

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
            
            logger.info(f"タイマー開始リクエスト: timer_id={timer_id}")
            
            # タイマー情報取得
            timer = Timer.objects.get(id=timer_id)
            total_seconds = timer.duration_minutes * 60
            
            # セッションID生成
            session_id = str(uuid.uuid4())
            
            logger.info(f"タイマー開始: timer_id={timer_id}, duration={timer.duration_minutes}分, session_id={session_id}")
            
            # 🔧 新しいタスクでタイマー開始
            result = start_timer_session.delay(session_id, timer_id, total_seconds)
            
            # タスクの完了を待機（短時間）
            try:
                task_result = result.get(timeout=10)  # 10秒でタイムアウト
                logger.info(f"タイマー開始タスク完了: {task_result}")
            except Exception as e:
                logger.warning(f"タスク完了待機エラー（継続実行中）: {e}")
            
            return JsonResponse({
                'success': True,
                'session_id': session_id,
                'message': f'{timer.band.name}のタイマーを開始しました（{timer.duration_minutes}分）',
                'duration': timer.duration_minutes,
                'timer_name': timer.name,
                'band_name': timer.band.name
            })
            
        except Timer.DoesNotExist:
            logger.error(f"タイマーが見つかりません: timer_id={timer_id}")
            return JsonResponse({'success': False, 'message': 'タイマーが見つかりません'})
        except json.JSONDecodeError:
            logger.error("JSONデコードエラー")
            return JsonResponse({'success': False, 'message': '不正なJSONデータです'})
        except Exception as e:
            logger.error(f"タイマー開始エラー: {e}")
            return JsonResponse({'success': False, 'message': f'エラーが発生しました: {str(e)}'})
    
    return JsonResponse({'success': False, 'message': 'POSTメソッドが必要です'})

def timer_status(request, session_id):
    """タイマー状態取得API"""
    try:
        logger.debug(f"タイマー状態取得: session_id={session_id}")
        
        # 🔧 同期でタイマー状態取得
        status = get_timer_status.delay(session_id).get(timeout=5)
        
        return JsonResponse({
            'success': True,
            'status': status
        })
    except Exception as e:
        logger.error(f"タイマー状態取得エラー: session_id={session_id}, error={e}")
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

@csrf_exempt
def pause_timer(request, session_id):
    """タイマー一時停止API"""
    if request.method == 'POST':
        try:
            result = pause_timer_session.delay(session_id).get(timeout=5)
            return JsonResponse(result)
        except Exception as e:
            logger.error(f"タイマー一時停止エラー: {e}")
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'POSTメソッドが必要です'})

@csrf_exempt  
def resume_timer(request, session_id):
    """タイマー再開API"""
    if request.method == 'POST':
        try:
            result = resume_timer_session.delay(session_id).get(timeout=5)
            return JsonResponse(result)
        except Exception as e:
            logger.error(f"タイマー再開エラー: {e}")
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'POSTメソッドが必要です'})

def test_celery_connection(request):
    """Celery接続テスト用エンドポイント"""
    try:
        result = test_celery.delay()
        task_result = result.get(timeout=10)
        
        return JsonResponse({
            'success': True,
            'message': 'Celery接続成功',
            'result': task_result,
            'task_id': result.id
        })
    except Exception as e:
        logger.error(f"Celeryテストエラー: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Celery接続エラー: {str(e)}'
        })