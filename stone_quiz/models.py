from django.db import models
from django.contrib.auth import get_user_model
from Stone.models import StoneCategory

User = get_user_model()

class QuizQuestion(models.Model):
    QUESTION_TYPE_CHOICES = [
        ('single', 'Один вариант'),
        ('multiple', 'Несколько вариантов'),
    ]
    
    question = models.CharField(max_length=500, verbose_name='Вопрос')
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES, default='single')
    order = models.IntegerField(default=0, verbose_name='Порядок')
    
    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ['order']
    
    def __str__(self):
        return self.question

class QuizAnswer(models.Model):
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, related_name='answers')
    answer = models.CharField(max_length=200, verbose_name='Ответ')
    granite_weight = models.IntegerField(default=0, verbose_name='Гранит')
    marble_weight = models.IntegerField(default=0, verbose_name='Мрамор')
    quartzite_weight = models.IntegerField(default=0, verbose_name='Кварцит')
    travertine_weight = models.IntegerField(default=0, verbose_name='Травертин')
    slate_weight = models.IntegerField(default=0, verbose_name='Сланец')
    onyx_weight = models.IntegerField(default=0, verbose_name='Оникс')
    image = models.ImageField(upload_to='quiz/', blank=True, null=True, verbose_name='Изображение')
    order = models.IntegerField(default=0, verbose_name='Порядок')
    
    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'
        ordering = ['order']
    
    def __str__(self):
        return self.answer

class QuizResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_results', verbose_name='Пользователь')
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    email = models.EmailField(verbose_name='Email')
    phone = models.CharField(max_length=20, verbose_name='Телефон', blank=True)
    answers = models.JSONField(verbose_name='Ответы')
    
    granite_score = models.IntegerField(default=0, verbose_name='Гранит')
    marble_score = models.IntegerField(default=0, verbose_name='Мрамор')
    quartzite_score = models.IntegerField(default=0, verbose_name='Кварцит')
    travertine_score = models.IntegerField(default=0, verbose_name='Травертин')
    slate_score = models.IntegerField(default=0, verbose_name='Сланец')
    onyx_score = models.IntegerField(default=0, verbose_name='Оникс')
    
    recommended_category = models.ForeignKey(StoneCategory, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Рекомендуемая категория')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата прохождения')
    
    class Meta:
        verbose_name = 'Результат теста'
        verbose_name_plural = 'Результаты тестов'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.last_name} {self.first_name} - {self.created_at.strftime('%d.%m.%Y')}"