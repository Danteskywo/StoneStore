from django import forms
from .models import Feedback, CountertopOrder, Stone

CHOICE_TYPE = [
    ("review", "Отзыв"),
    ("question", "Вопрос"),
]

class UserForm(forms.Form):
    name = forms.CharField(
        label="Ваше Имя",
        max_length=30,
        widget=forms.TextInput(attrs={'placeholder': 'Введите ваше имя'})
    )
    numTel = forms.CharField(
        label='Номер телефона',
        max_length=20,
        widget=forms.TextInput(attrs={'placeholder': '+7 (___) ___-__-__'})
    )
    adress = forms.CharField(
        label='Адрес',
        required=False,
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Ваш адрес (необязательно)'})
    )
    langs = forms.ChoiceField(
        choices=CHOICE_TYPE,
        label="Тип обращения",
        widget=forms.RadioSelect,
        initial="review"
    )
    message = forms.CharField(
        label="Ваше сообщение",
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Напишите ваш отзыв или вопрос'})
    )
    rating = forms.ChoiceField(
        choices=[(5, '★★★★★'), (4, '★★★★'), (3, '★★★'), (2, '★★'), (1, '★')],
        label="Оценка",
        required=False,
        widget=forms.RadioSelect()
    )

class CountertopOrderForm(forms.ModelForm):
    class Meta:
        model = CountertopOrder
        fields = ['stone', 'length', 'width', 'thickness', 'edge_type', 'sink_type', 
                  'cutouts', 'customer_name', 'customer_phone', 'customer_email', 
                  'customer_address', 'comment']
        widgets = {
            'stone': forms.Select(attrs={'class': 'form-select'}),
            'length': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.5'}),
            'width': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.5'}),
            'thickness': forms.Select(attrs={'class': 'form-select'}),
            'edge_type': forms.Select(attrs={'class': 'form-select'}),
            'sink_type': forms.Select(attrs={'class': 'form-select'}),
            'cutouts': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Иванов Иван'}),
            'customer_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (999) 123-45-67'}),
            'customer_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}),
            'customer_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'stone': 'Выберите камень',
            'length': 'Длина (м)',
            'width': 'Ширина (м)',
            'thickness': 'Толщина (мм)',
            'edge_type': 'Тип кромки',
            'sink_type': 'Тип мойки',
            'cutouts': 'Вырезы',
            'customer_name': 'Ваше имя',
            'customer_phone': 'Телефон',
            'customer_email': 'Email',
            'customer_address': 'Адрес доставки',
            'comment': 'Комментарий к заказу',
        }