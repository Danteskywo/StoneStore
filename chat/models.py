from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Пользователь')
    session_key = models.CharField(max_length=40, blank=True, verbose_name='Ключ сессии')
    operator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_chats', verbose_name='Оператор')
    
    STATUS_CHOICES = [
        ('waiting', 'Ожидание'),
        ('active', 'Активен'),
        ('closed', 'Закрыт'),
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting', verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлен')
    
    class Meta:
        verbose_name = 'Сессия чата'
        verbose_name_plural = 'Сессии чатов'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Чат #{self.id} - {self.get_status_display()}"

class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages', verbose_name='Сессия')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Пользователь')
    message = models.TextField(verbose_name='Сообщение')
    is_operator = models.BooleanField(default=False, verbose_name='Сообщение оператора')
    is_read = models.BooleanField(default=False, verbose_name='Прочитано')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    
    class Meta:
        verbose_name = 'Сообщение чата'
        verbose_name_plural = 'Сообщения чата'
        ordering = ['created_at']
    
    def __str__(self):
        return f"Сообщение #{self.id} от {self.created_at.strftime('%d.%m.%Y %H:%M')}"