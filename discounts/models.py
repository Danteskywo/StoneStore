from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from Stone.models import Stone, StoneCategory

class PromoCode(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percent', 'Процент'),
        ('fixed', 'Фиксированная сумма'),
    ]
    
    code = models.CharField(max_length=50, unique=True, verbose_name='Промокод')
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES, default='percent')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Скидка')
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Минимальная сумма заказа')
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Максимальная скидка')
    usage_limit = models.IntegerField(default=1, verbose_name='Лимит использований')
    usage_count = models.IntegerField(default=0, verbose_name='Использовано раз')
    per_user_limit = models.IntegerField(default=1, verbose_name='Лимит на пользователя')
    applicable_stones = models.ManyToManyField(Stone, blank=True, verbose_name='Доступные камни')
    applicable_categories = models.ManyToManyField(StoneCategory, blank=True, verbose_name='Доступные категории')
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Промокод'
        verbose_name_plural = 'Промокоды'
    
    def __str__(self):
        return self.code
    
    def is_valid(self, user=None, order_amount=None):
        from django.utils import timezone
        now = timezone.now()
        
        if not self.is_active:
            return False, 'Промокод неактивен'
        
        if now < self.valid_from or now > self.valid_to:
            return False, 'Срок действия промокода истек'
        
        if self.usage_limit and self.usage_count >= self.usage_limit:
            return False, 'Лимит использований исчерпан'
        
        if order_amount and self.min_order_amount and order_amount < self.min_order_amount:
            return False, f'Минимальная сумма заказа: {self.min_order_amount} ₽'
        
        return True, 'Промокод действителен'
    
    def calculate_discount(self, amount):
        if self.discount_type == 'percent':
            discount = amount * self.discount_value / 100
        else:
            discount = self.discount_value
        
        if self.max_discount_amount and discount > self.max_discount_amount:
            discount = self.max_discount_amount
        
        return discount

class DiscountRule(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percent', 'Процент'),
        ('fixed', 'Фиксированная сумма'),
    ]
    
    CONDITION_TYPE_CHOICES = [
        ('order_amount', 'Сумма заказа'),
        ('stone_count', 'Количество камней'),
        ('category', 'Категория'),
        ('first_order', 'Первый заказ'),
        ('birthday', 'День рождения'),
    ]
    
    name = models.CharField(max_length=200, verbose_name='Название')
    condition_type = models.CharField(max_length=20, choices=CONDITION_TYPE_CHOICES)
    condition_value = models.CharField(max_length=255, help_text='Значение условия')
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0, help_text='Приоритет (чем выше, тем важнее)')
    
    class Meta:
        verbose_name = 'Правило скидки'
        verbose_name_plural = 'Правила скидок'
    
    def __str__(self):
        return self.name