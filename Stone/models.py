from django.db import models

###########  Аунтификация ##############




class Feedback(models.Model):

    CHOICE_TYPE = [
        ("review", "Отзыв"),
        ("question", "Вопрос"),
    ]

    RATING_CHOICES = [
        (1,'1 звезда'),
        (2,'2 звезда'),
        (3,'3 звезда'),
        (4,'4 звезда'),
        (5,'5 звезда'),
    ]

    request_type = models.CharField(
        max_length=10,
        choices=CHOICE_TYPE,
        default='review',
        verbose_name='Тип обращения'
    )

    name = models.CharField(
        max_length=30,
        verbose_name='Имя'
        )
    numTel = models.CharField(
        max_length=20,
        verbose_name='номер телефона'
        )
    adress = models.TextField(blank=True, verbose_name='Адрес')
    message = models.TextField(verbose_name='Сообщение')
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        null=True,
        blank=True,
        verbose_name='Оценка'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
        )

    def __str__(self):
        return f"{self.name}-{self.created_at}"
    
    class Meta:
        verbose_name = "Обратная связь"
        verbose_name_plural = 'обратная связь'


CHOICE_PHONE = [
    ("site","Оставить на сайте"),
    ("call","Позвонить"),
]

class ByModels(models.Model):
    name = models.CharField(
        max_length=30,
        verbose_name='Имя'
        )
    numTel = models.CharField(
        max_length=20,
        verbose_name='номер телефона'
        )
    adress = models.TextField(
        blank=True,
        verbose_name='Адрес'
        )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
        )
    request_by = models.CharField(
        max_length=10,
        choices= CHOICE_PHONE,
        default='call',
        verbose_name='Заказать звонок'
    )
    def __str__(self):
        return f"{self.name}-{self.created_at}"
    
class Pokupka(models.Model):

        STATUS_CHOICES = [
            ("new", 'Новый заказ'),
            ("processing", 'Заказ в обработке'),
            ('completed','Заказ завершен'),
            ('cancelled','Заказ отменен'),
        ]

        by_models_order = models.ForeignKey(
            ByModels,
            on_delete=models.SET_NULL,
            null=True,
            blank=True,
            verbose_name='Связанный заказ',
            related_name='pokupki'
        )
        product_name = models.CharField(
            max_length=100,
            verbose_name='Название товара'
        )
        quantity = models.PositiveIntegerField(
            default=1,
            verbose_name='Количество',
        )
        price = models.DecimalField(
            max_digits=10,
            decimal_places=2,
            verbose_name='Цена за единицу'
        )

        customer_name = models.CharField(
            max_length=30,
            verbose_name='Имя покупателя'
        )
        phone = models.CharField(
            max_length=20,
            verbose_name='Телефон'
        )
        delivery_address = models.TextField(
            blank=True,
            verbose_name='Адрес доставки'
        )
        status = models.CharField(
            max_length=20,
            choices=STATUS_CHOICES,
            default='new',
            verbose_name='Статус'
        )
        created_at = models.DateTimeField(
            auto_now_add=True,
            verbose_name='Дата создания'
        )
        updated_at = models.DateTimeField(
            auto_now = True,
            verbose_name="Дата обновления"
        )

        class Meta:
            verbose_name = 'Покупка'
            verbose_name_plural = 'Покупки'
            ordering = ['-created_at']
        def __str__(self):
            return f'{self.product_name} - {self.customer_name} - {self.created_at.strftime("%d.%m.%Y")}'
        @property
        def total_price(self):
            return self.quantity * self.price
        
        def get_status_display_colored(self):
            colors = {
                "new":'green',
                "processing": 'orange',
                'completed':'blue',
                'cancelled':'red',
            }
            return f'<span style="color: {colors.get(self.status, "black")};">{self.get_status_display()}</span>'



    