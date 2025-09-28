from celery import shared_task
from django.core.cache import cache
from django.utils import timezone
from datetime import datetime, timedelta
import logging
import json

logger = logging.getLogger(__name__)

@shared_task
def test_celery():
    """Celery動作テスト用タスク"""
    logger.info("Celeryタスクが正常に動作しています！")
    return "Celery is working!"

@shared_task(bind=True)
def start_timer_session(self, session_id, timer_id, total_seconds):
    """
    タイマーセッション開始
    長時間実行ではなく、開始時刻を記録するだけ
    """
    logger.info(f"タイマーセッション開始: session_id={session_id}, timer_id={timer_id}, total_seconds={total_seconds}")
    
    # 開始時刻を記録
    start_time = timezone.now()
    end_time = start_time + timedelta(seconds=total_seconds)
    
    cache_key = f"timer_session:{session_id}"
    
    # セッション状態をキャッシュに保存
    session_data = {
        'status': 'running',
        'timer_id': timer_id,
        'start_time': start_time.isoformat(),
        'end_time': end_time.isoformat(),
        'total_seconds': total_seconds,
        'created_at': timezone.now().isoformat()
    }
    
    # 1時間キャッシュ（十分なリハーサル時間）
    cache.set(cache_key, session_data, timeout=3600)
    
    logger.info(f"タイマーセッション開始完了: session_id={session_id}")
    
    # 定期チェックタスクを開始
    check_timer_completion.apply_async(args=[session_id], countdown=5)
    
    return {
        'success': True,
        'session_id': session_id,
        'start_time': start_time.isoformat(),
        'end_time': end_time.isoformat()
    }

@shared_task(bind=True)
def check_timer_completion(self, session_id):
    """
    タイマー完了チェック（定期実行）
    リアルタイムではなく定期的にチェック
    """
    cache_key = f"timer_session:{session_id}"
    session_data = cache.get(cache_key)
    
    if not session_data:
        logger.warning(f"セッションが見つかりません: {session_id}")
        return
    
    if session_data.get('status') != 'running':
        logger.info(f"セッションが停止中: {session_id}")
        return
    
    # 現在時刻と終了時刻を比較
    now = timezone.now()
    end_time = datetime.fromisoformat(session_data['end_time'].replace('Z', '+00:00'))
    
    if timezone.is_aware(end_time):
        end_time = timezone.make_naive(end_time, timezone.utc)
        now = timezone.make_naive(now, timezone.utc)
    
    if now >= end_time:
        # タイマー完了
        session_data['status'] = 'completed'
        session_data['completed_at'] = timezone.now().isoformat()
        cache.set(cache_key, session_data, timeout=3600)
        
        logger.info(f"タイマー完了: session_id={session_id}")
        
        # WebSocket通知（将来実装）
        # notify_timer_completion.delay(session_id)
        
        return {'status': 'completed', 'session_id': session_id}
    else:
        # まだ継続中 - 10秒後に再チェック
        remaining_seconds = (end_time - now).total_seconds()
        session_data['remaining_seconds'] = max(0, int(remaining_seconds))
        cache.set(cache_key, session_data, timeout=3600)
        
        # 10秒後に再チェック
        check_timer_completion.apply_async(args=[session_id], countdown=10)
        
        return {'status': 'running', 'remaining_seconds': remaining_seconds}

@shared_task
def get_timer_status(session_id):
    """
    タイマーの現在状態を取得（同期処理）
    """
    cache_key = f"timer_session:{session_id}"
    session_data = cache.get(cache_key)
    
    if not session_data:
        return {'status': 'not_found', 'message': 'セッションが見つかりません'}
    
    # 現在の残り時間を計算
    if session_data.get('status') == 'running':
        now = timezone.now()
        end_time_str = session_data.get('end_time')
        
        if end_time_str:
            try:
                end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
                if timezone.is_aware(end_time):
                    end_time = timezone.make_naive(end_time, timezone.utc)
                    now = timezone.make_naive(now, timezone.utc)
                
                remaining_seconds = max(0, int((end_time - now).total_seconds()))
                session_data['remaining_seconds'] = remaining_seconds
                
                # 残り時間が0になった場合は完了状態に更新
                if remaining_seconds == 0:
                    session_data['status'] = 'completed'
                    cache.set(cache_key, session_data, timeout=3600)
                    
            except (ValueError, TypeError) as e:
                logger.error(f"時刻解析エラー: {e}")
                session_data['remaining_seconds'] = 0
    
    return session_data

@shared_task
def pause_timer_session(session_id):
    """タイマー一時停止"""
    cache_key = f"timer_session:{session_id}"
    session_data = cache.get(cache_key)
    
    if not session_data:
        return {'success': False, 'message': 'セッションが見つかりません'}
    
    if session_data.get('status') != 'running':
        return {'success': False, 'message': 'タイマーが実行中ではありません'}
    
    # 一時停止時刻を記録
    session_data['status'] = 'paused'
    session_data['paused_at'] = timezone.now().isoformat()
    cache.set(cache_key, session_data, timeout=3600)
    
    logger.info(f"タイマー一時停止: session_id={session_id}")
    return {'success': True, 'status': 'paused'}

@shared_task  
def resume_timer_session(session_id):
    """タイマー再開"""
    cache_key = f"timer_session:{session_id}"
    session_data = cache.get(cache_key)
    
    if not session_data:
        return {'success': False, 'message': 'セッションが見つかりません'}
    
    if session_data.get('status') != 'paused':
        return {'success': False, 'message': 'タイマーが一時停止中ではありません'}
    
    # 一時停止時間を計算して終了時刻を延長
    now = timezone.now()
    paused_at = datetime.fromisoformat(session_data['paused_at'].replace('Z', '+00:00'))
    if timezone.is_aware(paused_at):
        paused_at = timezone.make_naive(paused_at, timezone.utc)
        now = timezone.make_naive(now, timezone.utc)
    
    pause_duration = (now - paused_at).total_seconds()
    
    # 終了時刻を延長
    end_time = datetime.fromisoformat(session_data['end_time'].replace('Z', '+00:00'))
    if timezone.is_aware(end_time):
        end_time = timezone.make_naive(end_time, timezone.utc)
    
    new_end_time = end_time + timedelta(seconds=pause_duration)
    
    session_data['status'] = 'running'
    session_data['end_time'] = new_end_time.isoformat()
    session_data.pop('paused_at', None)
    cache.set(cache_key, session_data, timeout=3600)
    
    # 定期チェック再開
    check_timer_completion.apply_async(args=[session_id], countdown=5)
    
    logger.info(f"タイマー再開: session_id={session_id}")
    return {'success': True, 'status': 'running'}