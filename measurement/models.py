from django.db import models
from Stone.models import Stone

class MeasurementRequest(models.Model):
    name = models.CharField(max_length=100, verbose_name='Имя')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    email = models.EmailField(blank=True, verbose_name='Email')
    address = models.TextField(verbose_name='Адрес объекта')
    stone = models.ForeignKey(Stone, on_delete=models.SET_NULL, null=True, blank=True)
    product_type = models.CharField(max_length=50, choices=[
        ('countertop', 'Столешница'),
        ('window_sill', 'Подоконник'),
        ('stairs', 'Ступени'),
        ('other', 'Другое')
    ], default='countertop')
    preferred_date = models.DateField(null=True, blank=True)
    preferred_time = models.CharField(max_length=20, blank=True)
    
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('scheduled', 'Запланирован'),
        ('completed', 'Выполнен'),
        ('cancelled', 'Отменен'),
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Запрос на замер'
        verbose_name_plural = 'Запросы на замер'
    
    def __str__(self):
        return f"Замер #{self.id} - {self.name}"