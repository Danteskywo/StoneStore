from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class StoneCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название категории')
    slug = models.SlugField(unique=True, verbose_name='URL')
    description = models.TextField(blank=True, verbose_name='Описание')
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name='Изображение')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок сортировки')
    
    class Meta:
        verbose_name = 'Категория камня'
        verbose_name_plural = 'Категории камней'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name

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
    
    name = models.CharField(max_length=200, verbose_name='Название камня')
    slug = models.SlugField(unique=True, verbose_name='URL')
    category = models.ForeignKey(StoneCategory, on_delete=models.CASCADE, related_name='stones', verbose_name='Категория')
    
    description = models.TextField(verbose_name='Описание')
    characteristics = models.TextField(blank=True, verbose_name='Характеристики')
    
    main_image = models.ImageField(upload_to='stones/', verbose_name='Главное фото')
    
    price_per_sqm = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена за м²')
    
    hardness = models.PositiveIntegerField(help_text='По шкале Мооса (1-10)', validators=[MinValueValidator(1), MaxValueValidator(10)], verbose_name='Твердость')
    frost_resistance = models.BooleanField(default=True, verbose_name='Морозостойкость')
    water_absorption = models.DecimalField(max_digits=5, decimal_places=2, help_text='В %', verbose_name='Водопоглощение')
    
    available_finishes = models.CharField(max_length=200, help_text='Через запятую', verbose_name='Доступные обработки')
    available_thickness = models.CharField(max_length=50, help_text='Через запятую', verbose_name='Доступные толщины')
    
    in_stock = models.BooleanField(default=True, verbose_name='В наличии')
    stock_quantity = models.PositiveIntegerField(default=0, verbose_name='Количество на складе (м²)')
    
    is_popular = models.BooleanField(default=False, verbose_name='Популярный')
    is_new = models.BooleanField(default=False, verbose_name='Новинка')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Камень'
        verbose_name_plural = 'Камни'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_available_finishes_list(self):
        return [f.strip() for f in self.available_finishes.split(',')]
    
    def get_available_thickness_list(self):
        return [int(t.strip()) for t in self.available_thickness.split(',')]

class StoneImage(models.Model):
    stone = models.ForeignKey(Stone, on_delete=models.CASCADE, related_name='images', verbose_name='Камень')
    image = models.ImageField(upload_to='stones/gallery/', verbose_name='Изображение')
    is_main = models.BooleanField(default=False, verbose_name='Главное')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')
    
    class Meta:
        verbose_name = 'Изображение камня'
        verbose_name_plural = 'Изображения камней'
        ordering = ['-is_main', 'order']
    
    def __str__(self):
        return f"{self.stone.name} - {self.order}"

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
    
    stone = models.ForeignKey(Stone, on_delete=models.CASCADE, verbose_name='Камень')
    
    length = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='Длина (м)')
    width = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='Ширина (м)')
    thickness = models.PositiveIntegerField(choices=Stone.THICKNESS_CHOICES, verbose_name='Толщина (мм)')
    
    edge_type = models.CharField(max_length=20, choices=EDGE_CHOICES, default='straight', verbose_name='Тип кромки')
    sink_type = models.CharField(max_length=20, choices=SINK_CHOICES, default='none', verbose_name='Тип мойки')
    cutouts = models.TextField(blank=True, help_text='Описание вырезов под плиту и т.д.', verbose_name='Вырезы')
    
    customer_name = models.CharField(max_length=100, verbose_name='Имя')
    customer_phone = models.CharField(max_length=20, verbose_name='Телефон')
    customer_email = models.EmailField(blank=True, verbose_name='Email')
    customer_address = models.TextField(verbose_name='Адрес')
    
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('processing', 'В обработке'),
        ('measurement', 'Замер'),
        ('production', 'Производство'),
        ('delivery', 'Доставка'),
        ('completed', 'Выполнен'),
        ('cancelled', 'Отменен'),
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата заказа')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Заказ столешницы'
        verbose_name_plural = 'Заказы столешниц'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Заказ #{self.id} - {self.customer_name}"
    
    def calculate_area(self):
        """Расчет площади в м²"""
        return float(self.length) * float(self.width)
    
    def calculate_price(self):
        """Расчет цены"""
        return self.calculate_area() * float(self.stone.price_per_sqm)

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
    
    request_type = models.CharField(
        max_length=10,
        choices=CHOICE_TYPE,
        default='review',
        verbose_name='Тип обращения'
    )
    
    name = models.CharField(max_length=30, verbose_name='Имя')
    numTel = models.CharField(max_length=20, verbose_name='Номер телефона')
    adress = models.TextField(blank=True, verbose_name='Адрес')
    message = models.TextField(verbose_name='Сообщение')
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        null=True,
        blank=True,
        verbose_name='Оценка'
    )
    
    order = models.ForeignKey(CountertopOrder, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Заказ')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    is_published = models.BooleanField(default=True, verbose_name='Опубликовано')
    
    def __str__(self):
        return f"{self.name} - {self.created_at}"
    
    class Meta:
        verbose_name = "Обратная связь"
        verbose_name_plural = 'Обратная связь'
        ordering = ['-created_at']