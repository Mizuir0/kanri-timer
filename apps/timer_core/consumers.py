import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Band

logger = logging.getLogger(__name__)

class TimerConsumer(AsyncWebsocketConsumer):
    """タイマー用WebSocketコンシューマー"""
    
    async def connect(self):
        """WebSocket接続時の処理"""
        self.band_id = self.scope['url_route']['kwargs']['band_id']
        self.room_group_name = f'timer_band_{self.band_id}'
        
        # グループに参加
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # 接続を受け入れ
        await self.accept()
        
        logger.info(f"WebSocket接続: band_id={self.band_id}, channel={self.channel_name}")
        
        # 接続確認メッセージ送信
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': f'バンド {self.band_id} のタイマーに接続しました',
            'band_id': self.band_id
        }))

    async def disconnect(self, close_code):
        """WebSocket切断時の処理"""
        # グループから離脱
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        logger.info(f"WebSocket切断: band_id={self.band_id}, code={close_code}")

    async def receive(self, text_data):
        """クライアントからのメッセージ受信"""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')
            
            if message_type == 'ping':
                # ピングに対してポング応答
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': text_data_json.get('timestamp')
                }))
                
            elif message_type == 'timer_status_request':
                # タイマー状態要求（将来の実装用）
                await self.send(text_data=json.dumps({
                    'type': 'timer_status_response',
                    'message': 'タイマー状態機能は開発中です'
                }))
                
        except json.JSONDecodeError:
            # JSONパースエラー
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': '不正なメッセージ形式です'
            }))

    async def timer_update(self, event):
        """
        グループからのタイマー更新メッセージを送信
        Celeryタスクから呼び出される予定
        """
        await self.send(text_data=json.dumps({
            'type': 'timer_update',
            'data': event['data']
        }))

    async def timer_completed(self, event):
        """タイマー完了通知"""
        await self.send(text_data=json.dumps({
            'type': 'timer_completed',
            'data': event['data']
        }))

    @database_sync_to_async
    def get_band_info(self, band_id):
        """バンド情報取得（非同期対応）"""
        try:
            band = Band.objects.get(id=band_id)
            return {'id': band.id, 'name': band.name}
        except Band.DoesNotExist:
            return None