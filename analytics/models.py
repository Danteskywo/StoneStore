from django.db import models
from django.utils import timezone

class PageView(models.Model):
    url = models.CharField(max_length=500)
    referrer = models.CharField(max_length=500, blank=True)
    user_agent = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField()
    session_key = models.CharField(max_length=40, blank=True)
    user_id = models.IntegerField(null=True, blank=True)
    viewed_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = 'Просмотр'
        verbose_name_plural = 'Просмотры'
    
    def __str__(self):
        return f"{self.url} - {self.viewed_at}"

class EventLog(models.Model):
    EVENT_TYPES = [
        ('view', 'Просмотр'),
        ('click', 'Клик'),
        ('search', 'Поиск'),
        ('order', 'Заказ'),
        ('feedback', 'Отзыв'),
        ('calculation', 'Расчет'),
    ]
    
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    category = models.CharField(max_length=100)
    action = models.CharField(max_length=100)
    label = models.CharField(max_length=200, blank=True)
    value = models.IntegerField(null=True, blank=True)
    url = models.CharField(max_length=500, blank=True)
    session_key = models.CharField(max_length=40, blank=True)
    user_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = 'Событие'
        verbose_name_plural = 'События'
    
    def __str__(self):
        return f"{self.event_type} - {self.action}"