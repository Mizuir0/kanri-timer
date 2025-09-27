from django.db import models

class Band(models.Model):
    """バンド情報"""
    name = models.CharField('バンド名', max_length=100)
    description = models.TextField('説明', blank=True)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    
    class Meta:
        verbose_name = 'バンド'
        verbose_name_plural = 'バンド一覧'
    
    def __str__(self):
        return self.name

class Timer(models.Model):
    """タイマー情報"""
    band = models.ForeignKey(Band, on_delete=models.CASCADE, verbose_name='バンド')
    name = models.CharField('タイマー名', max_length=100)
    duration_minutes = models.IntegerField('時間（分）', default=15)
    order = models.PositiveIntegerField('順序', default=1)
    
    # 管理者情報（既存アプリと同じ形式）
    manager1 = models.CharField('管理者1', max_length=50, blank=True)
    manager2 = models.CharField('管理者2', max_length=50, blank=True)
    manager3 = models.CharField('管理者3', max_length=50, blank=True)
    
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    is_active = models.BooleanField('有効', default=True)
    
    class Meta:
        verbose_name = 'タイマー'
        verbose_name_plural = 'タイマー一覧'
        ordering = ['band', 'order']  # バンド別、順序順でソート
    
    def __str__(self):
        return f"{self.band.name} - {self.name} ({self.duration_minutes}分)"