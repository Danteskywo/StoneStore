from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    city = models.CharField(max_length=100, blank=True)
    interests = models.JSONField(default=list)
    
    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'
    
    def __str__(self):
        return self.email

class NewsletterCampaign(models.Model):
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=200)
    content = models.TextField()
    template = models.CharField(max_length=100, default='default')
    
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('scheduled', 'Запланирована'),
        ('sending', 'Отправляется'),
        ('sent', 'Отправлена'),
        ('cancelled', 'Отменена'),
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    scheduled_time = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    total_recipients = models.IntegerField(default=0)
    sent_count = models.IntegerField(default=0)
    opened_count = models.IntegerField(default=0)
    clicked_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'
    
    def __str__(self):
        return self.title

class NewsletterTracking(models.Model):
    subscriber = models.ForeignKey(Subscriber, on_delete=models.CASCADE)
    campaign = models.ForeignKey(NewsletterCampaign, on_delete=models.CASCADE)
    opened_at = models.DateTimeField(null=True, blank=True)
    opened_count = models.IntegerField(default=0)
    clicked_at = models.DateTimeField(null=True, blank=True)
    clicked_count = models.IntegerField(default=0)
    clicked_links = models.JSONField(default=list)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Отслеживание'
        verbose_name_plural = 'Отслеживания'
        unique_together = ['subscriber', 'campaign']