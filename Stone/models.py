from django.db import models


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


