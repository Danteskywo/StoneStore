from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import os

def validate_image_size(image):
    """Валидация размера изображения (макс 5MB)"""
    if image.size > 5 * 1024 * 1024:
        raise ValidationError('Размер изображения не должен превышать 5MB')
    
    # Проверка расширения файла
    ext = os.path.splitext(image.name)[1].lower()
    if ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
        raise ValidationError('Поддерживаются только изображения форматов: JPG, PNG, GIF, WEBP')

class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    avatar = models.ImageField(
        upload_to='avatars/', 
        blank=True, 
        null=True, 
        verbose_name='Аватар',
        validators=[validate_image_size]
    )
    birth_date = models.DateField(null=True, blank=True, verbose_name='Дата рождения')
    address = models.TextField(blank=True, verbose_name='Адрес')
    email_notifications = models.BooleanField(default=True, verbose_name='Email-уведомления')
    sms_notifications = models.BooleanField(default=False, verbose_name='SMS-уведомления')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        permissions = [
            ("can_view_analytics", "Может просматривать аналитику"),
        ]
    
    def __str__(self):
        return self.username
    
    def get_full_name(self):
        """Возвращает полное имя пользователя"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

class StoneCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название категории')
    slug = models.SlugField(unique=True, verbose_name='URL')
    description = models.TextField(blank=True, verbose_name='Описание')
    image = models.ImageField(
        upload_to='categories/', 
        blank=True, 
        null=True, 
        verbose_name='Изображение',
        validators=[validate_image_size]
    )
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок сортировки')
    
    class Meta:
        verbose_name = 'Категория камня'
        verbose_name_plural = 'Категории камней'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Stone(models.Model):
    FINISH_CHOICES = [
        ('polished', 'Полированная'),
        ('matte', 'Матовая'),
        ('rough', 'Грубая'),
        ('leather', 'Кожаная'),
    ]
    
    THICKNESS_CHOICES = [
        (20, '20 мм'),
        (30, '30 мм'),
        (40, '40 мм'),
        (50, '50 мм'),
    ]
    
    name = models.CharField(max_length=200, verbose_name='Название камня', db_index=True)
    slug = models.SlugField(unique=True, verbose_name='URL', db_index=True)
    category = models.ForeignKey(
        StoneCategory, 
        on_delete=models.CASCADE, 
        related_name='stones', 
        verbose_name='Категория'
    )
    description = models.TextField(verbose_name='Описание')
    characteristics = models.TextField(blank=True, verbose_name='Характеристики')
    main_image = models.ImageField(
        upload_to='stones/', 
        verbose_name='Главное фото',
        validators=[validate_image_size]
    )
    price_per_sqm = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name='Цена за м²',
        validators=[MinValueValidator(0)]
    )
    hardness = models.PositiveIntegerField(
        help_text='По шкале Мооса (1-10)', 
        validators=[MinValueValidator(1), MaxValueValidator(10)], 
        verbose_name='Твердость'
    )
    frost_resistance = models.BooleanField(default=True, verbose_name='Морозостойкость')
    water_absorption = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        help_text='В %', 
        verbose_name='Водопоглощение',
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    available_finishes = models.CharField(
        max_length=200, 
        help_text='Через запятую', 
        verbose_name='Доступные обработки'
    )
    available_thickness = models.CharField(
        max_length=50, 
        help_text='Через запятую', 
        verbose_name='Доступные толщины'
    )
    in_stock = models.BooleanField(default=True, verbose_name='В наличии', db_index=True)
    stock_quantity = models.PositiveIntegerField(default=0, verbose_name='Количество на складе (м²)')
    is_popular = models.BooleanField(default=False, verbose_name='Популярный', db_index=True)
    is_new = models.BooleanField(default=False, verbose_name='Новинка', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления', db_index=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    # Цены для калькулятора
    cutting_price_per_m = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=500, 
        verbose_name='Цена резки за м.п.',
        validators=[MinValueValidator(0)]
    )
    edge_processing_prices = models.JSONField(default=dict, verbose_name='Цены на обработку кромки')
    sink_cutout_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=3000, 
        verbose_name='Цена выреза под мойку',
        validators=[MinValueValidator(0)]
    )
    hob_cutout_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=2500, 
        verbose_name='Цена выреза под плиту',
        validators=[MinValueValidator(0)]
    )
    installation_price_per_m = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=1500, 
        verbose_name='Цена монтажа за м.п.',
        validators=[MinValueValidator(0)]
    )
    
    class Meta:
        verbose_name = 'Камень'
        verbose_name_plural = 'Камни'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['category', 'in_stock']),
            models.Index(fields=['price_per_sqm']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_available_finishes_list(self):
        """Возвращает список доступных обработок"""
        if not self.available_finishes:
            return []
        return [f.strip() for f in self.available_finishes.split(',') if f.strip()]
    
    def get_available_thickness_list(self):
        """Возвращает список доступных толщин"""
        if not self.available_thickness:
            return []
        thicknesses = []
        for t in self.available_thickness.split(','):
            try:
                thicknesses.append(int(t.strip()))
            except ValueError:
                continue
        return thicknesses
    
    def get_edge_price(self, edge_type):
        """Возвращает цену для указанного типа кромки"""
        if not self.edge_processing_prices:
            return 0
        return float(self.edge_processing_prices.get(edge_type, 0))
    
    @property
    def is_available(self):
        """Проверяет доступность камня"""
        return self.in_stock and self.stock_quantity > 0

class StoneImage(models.Model):
    stone = models.ForeignKey(
        Stone, 
        on_delete=models.CASCADE, 
        related_name='images', 
        verbose_name='Камень'
    )
    image = models.ImageField(
        upload_to='stones/gallery/', 
        verbose_name='Изображение',
        validators=[validate_image_size]
    )
    is_main = models.BooleanField(default=False, verbose_name='Главное')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')
    
    class Meta:
        verbose_name = 'Изображение камня'
        verbose_name_plural = 'Изображения камней'
        ordering = ['-is_main', 'order']
    
    def __str__(self):
        return f"{self.stone.name} - {self.order}"
    
    def save(self, *args, **kwargs):
        # Если это главное изображение, снимаем флаг с других
        if self.is_main:
            StoneImage.objects.filter(stone=self.stone, is_main=True).update(is_main=False)
        super().save(*args, **kwargs)

class CountertopOrder(models.Model):
    EDGE_CHOICES = [
        ('straight', 'Прямой'),
        ('rounded', 'Закругленный'),
        ('bevel', 'Скос'),
    ]
    
    SINK_CHOICES = [
        ('none', 'Без мойки'),
        ('undermount', 'Врезная'),
        ('integrated', 'Интегрированная'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('processing', 'В обработке'),
        ('measurement', 'Замер'),
        ('production', 'Производство'),
        ('delivery', 'Доставка'),
        ('completed', 'Выполнен'),
        ('cancelled', 'Отменен'),
    ]
    
    stone = models.ForeignKey(Stone, on_delete=models.CASCADE, verbose_name='Камень')
    length = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        verbose_name='Длина (м)',
        validators=[MinValueValidator(0.1)]
    )
    width = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        verbose_name='Ширина (м)',
        validators=[MinValueValidator(0.1)]
    )
    thickness = models.PositiveIntegerField(choices=Stone.THICKNESS_CHOICES, verbose_name='Толщина (мм)')
    edge_type = models.CharField(max_length=20, choices=EDGE_CHOICES, default='straight', verbose_name='Тип кромки')
    sink_type = models.CharField(max_length=20, choices=SINK_CHOICES, default='none', verbose_name='Тип мойки')
    cutouts = models.TextField(blank=True, help_text='Описание вырезов под плиту и т.д.', verbose_name='Вырезы')
    customer_name = models.CharField(max_length=100, verbose_name='Имя')
    customer_phone = models.CharField(max_length=20, verbose_name='Телефон', db_index=True)
    customer_email = models.EmailField(blank=True, verbose_name='Email')
    customer_address = models.TextField(verbose_name='Адрес')
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name='Статус', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата заказа', db_index=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    # Поля для хранения рассчитанных значений
    total_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        verbose_name='Итоговая цена'
    )
    promo_code = models.CharField(max_length=50, blank=True, verbose_name='Промокод')
    discount_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        verbose_name='Скидка'
    )
    
    class Meta:
        verbose_name = 'Заказ столешницы'
        verbose_name_plural = 'Заказы столешниц'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['customer_phone']),
        ]
    
    def __str__(self):
        return f"Заказ #{self.id} - {self.customer_name}"
    
    def calculate_area(self):
        """Расчет площади"""
        return float(self.length) * float(self.width)
    
    def calculate_price(self):
        """Расчет базовой цены"""
        return self.calculate_area() * float(self.stone.price_per_sqm)
    
    def calculate_total_with_discount(self):
        """Расчет итоговой цены со скидкой"""
        base_price = self.calculate_price()
        return base_price - float(self.discount_amount)
    
    def save(self, *args, **kwargs):
        # Автоматический расчет цены при сохранении
        if not self.total_price:
            self.total_price = self.calculate_price()
        super().save(*args, **kwargs)

class Feedback(models.Model):
    CHOICE_TYPE = [
        ("review", "Отзыв"),
        ("question", "Вопрос"),
    ]
    
    RATING_CHOICES = [
        (1,'1 звезда'),
        (2,'2 звезды'),
        (3,'3 звезды'),
        (4,'4 звезды'),
        (5,'5 звезд'),
    ]
    
    MODERATION_CHOICES = [
        ('pending', 'На модерации'),
        ('approved', 'Одобрен'),
        ('rejected', 'Отклонен'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        verbose_name='Пользователь',
        related_name='feedbacks'
    )
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        verbose_name='Ответ на',
        related_name='replies'
    )
    
    request_type = models.CharField(
        max_length=10, 
        choices=CHOICE_TYPE, 
        default='review', 
        verbose_name='Тип обращения',
        db_index=True
    )
    name = models.CharField(max_length=30, verbose_name='Имя')
    numTel = models.CharField(max_length=20, verbose_name='Номер телефона', db_index=True)
    adress = models.TextField(blank=True, verbose_name='Адрес')
    message = models.TextField(verbose_name='Сообщение')
    rating = models.IntegerField(choices=RATING_CHOICES, null=True, blank=True, verbose_name='Оценка')
    
    image1 = models.ImageField(
        upload_to='reviews/', 
        blank=True, 
        null=True, 
        verbose_name='Фото 1',
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif', 'webp']), validate_image_size]
    )
    image2 = models.ImageField(
        upload_to='reviews/', 
        blank=True, 
        null=True, 
        verbose_name='Фото 2',
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif', 'webp']), validate_image_size]
    )
    image3 = models.ImageField(
        upload_to='reviews/', 
        blank=True, 
        null=True, 
        verbose_name='Фото 3',
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif', 'webp']), validate_image_size]
    )
    
    order = models.ForeignKey(
        CountertopOrder, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name='Заказ'
    )
    is_verified = models.BooleanField(default=False, verbose_name='Подтвержденный заказ')
    moderation_status = models.CharField(
        max_length=20, 
        choices=MODERATION_CHOICES, 
        default='pending', 
        verbose_name='Статус модерации',
        db_index=True
    )
    moderation_comment = models.TextField(blank=True, verbose_name='Комментарий модератора')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания', db_index=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    is_published = models.BooleanField(default=False, verbose_name='Опубликовано', db_index=True)
    
    class Meta:
        verbose_name = "Обратная связь"
        verbose_name_plural = 'обратная связь'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['moderation_status', 'is_published']),
            models.Index(fields=['request_type', 'rating']),
            models.Index(fields=['user', 'created_at']),
        ]
        permissions = [
            ("can_moderate_feedback", "Может модерировать отзывы"),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.created_at}"
    
    def can_delete(self, user):
        """Проверяет, может ли пользователь удалить этот отзыв"""
        if not user.is_authenticated:
            return False
        if user.is_staff or user.has_perm('Stone.can_moderate_feedback'):
            return True
        # Пользователь может удалить свой отзыв в течение 24 часов после создания
        if self.user == user and timezone.now() - self.created_at < timedelta(hours=24):
            return True
        return False
    
    def save(self, *args, **kwargs):
        # Проверка изменения номера телефона
        if self.pk:
            try:
                original = Feedback.objects.get(pk=self.pk)
                if original.numTel != self.numTel:
                    self.order = None
                    self.is_verified = False
            except Feedback.DoesNotExist:
                pass
        
        # Автоматическая привязка к заказу
        if self.numTel and not self.order:
            order = CountertopOrder.objects.filter(customer_phone=self.numTel).first()
            if order:
                self.order = order
                self.is_verified = True
        
        # Автоматическая публикация при одобрении
        if self.moderation_status == 'approved':
            self.is_published = True
        elif self.moderation_status == 'rejected':
            self.is_published = False
            
        super().save(*args, **kwargs)
    
    def save_with_user(self, user, *args, **kwargs):
        """Сохраняет с указанием пользователя для определения прав"""
        self.user = user if user.is_authenticated else None
        # Если пользователь - модератор или админ, сразу одобряем
        if user.is_authenticated and (user.is_staff or user.has_perm('Stone.can_moderate_feedback')):
            self.moderation_status = 'approved'
            self.is_published = True
        self.save(*args, **kwargs)

class Wishlist(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='wishlist'
    )
    stone = models.ForeignKey(Stone, on_delete=models.CASCADE, related_name='wishlist_users')
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        unique_together = ['user', 'stone']
        ordering = ['-added_at']
        indexes = [
            models.Index(fields=['user', 'added_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.stone.name}"

class Comparison(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    session_key = models.CharField(max_length=40, blank=True, db_index=True)
    stones = models.ManyToManyField(Stone, related_name='comparisons')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Сравнение'
        verbose_name_plural = 'Сравнения'
        indexes = [
            models.Index(fields=['session_key']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"Сравнение #{self.id}"
    
    def clean(self):
        """Валидация количества камней в сравнении"""
        if self.pk and self.stones.count() > 4:
            raise ValidationError('Можно сравнивать не более 4 камней')

class ContactMessage(models.Model):
    """Сообщения из формы контактов"""
    name = models.CharField(max_length=100, verbose_name='Имя')
    email = models.EmailField(verbose_name='Email')
    message = models.TextField(verbose_name='Сообщение')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата отправки')
    is_read = models.BooleanField(default=False, verbose_name='Прочитано')
    
    class Meta:
        verbose_name = 'Сообщение с контактов'
        verbose_name_plural = 'Сообщения с контактов'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.created_at.strftime('%d.%m.%Y %H:%M')}"