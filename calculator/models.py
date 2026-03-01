from django.db import models
from django.contrib.auth import get_user_model
from Stone.models import Stone

User = get_user_model()

class SavedCalculation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='calculations')
    stone = models.ForeignKey(Stone, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, verbose_name='Название расчета')
    length = models.DecimalField(max_digits=6, decimal_places=2)
    width = models.DecimalField(max_digits=6, decimal_places=2)
    thickness = models.IntegerField()
    edge_type = models.CharField(max_length=50)
    has_sink_cutout = models.BooleanField(default=False)
    has_hob_cutout = models.BooleanField(default=False)
    need_installation = models.BooleanField(default=False)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Сохраненный расчет'
        verbose_name_plural = 'Сохраненные расчеты'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.total_price}₽"