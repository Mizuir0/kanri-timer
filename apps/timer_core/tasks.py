from celery import shared_task
from django.core.cache import cache
from django.utils import timezone
import time
import logging

logger = logging.getLogger(__name__)

@shared_task
def test_celery():
    """Celery動作テスト用タスク"""
    logger.info("Celeryタスクが正常に動作しています！")
    return "Celery is working!"

@shared_task(bind=True)
def countdown_timer(self, session_id, total_seconds):
    """
    シンプルなカウントダウンタイマー
    Args:
        session_id: タイマーセッションID
        total_seconds: 総秒数
    """
    logger.info(f"タイマー開始: session_id={session_id}, total_seconds={total_seconds}")
    
    # 開始時刻を記録
    start_time = timezone.now().timestamp()
    cache_key = f"timer_session:{session_id}"
    
    # セッション状態をキャッシュに保存
    session_data = {
        'status': 'running',
        'start_time': start_time,
        'total_seconds': total_seconds,
        'remaining_seconds': total_seconds,
        'last_update': start_time
    }
    cache.set(cache_key, session_data, timeout=3600)  # 1時間キャッシュ
    
    # カウントダウン実行
    for remaining in range(total_seconds, 0, -1):
        # タスクがキャンセルされていないかチェック
        if self.is_revoked():
            logger.info(f"タイマーがキャンセルされました: session_id={session_id}")
            cache.delete(cache_key)
            return "Timer cancelled"
        
        # 現在時刻を更新
        current_time = timezone.now().timestamp()
        session_data['remaining_seconds'] = remaining
        session_data['last_update'] = current_time
        cache.set(cache_key, session_data, timeout=3600)
        
        logger.debug(f"タイマー進行中: session_id={session_id}, remaining={remaining}秒")
        time.sleep(1)  # 1秒待機
    
    # タイマー完了
    session_data['status'] = 'completed'
    session_data['remaining_seconds'] = 0
    cache.set(cache_key, session_data, timeout=3600)
    
    logger.info(f"タイマー完了: session_id={session_id}")
    return f"Timer completed for session {session_id}"

@shared_task
def get_timer_status(session_id):
    """
    タイマーの現在状態を取得
    Args:
        session_id: タイマーセッションID
    Returns:
        dict: タイマー状態
    """
    cache_key = f"timer_session:{session_id}"
    session_data = cache.get(cache_key)
    
    if not session_data:
        return {'status': 'not_found', 'message': 'セッションが見つかりません'}
    
    return session_data