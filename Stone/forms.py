from django import forms
from .models import Pokupka

CHOICE_TYPE = [
    ("review", "Отзыв"),
    ("question", "Вопрос"),
]

class UserForm(forms.Form):
    name = forms.CharField(
        label="Ваше Имя",
        max_length=30,
        widget=forms.TextInput()
    )
    numTel = forms.CharField(
        label='Номер телефона',
        max_length=20,
        widget=forms.TextInput()
    )
    adress = forms.CharField(
        label='Адрес',
        required=False,
        widget=forms.Textarea()
    )
    langs = forms.ChoiceField(
        choices=CHOICE_TYPE,
        label="Тип обращения",
        widget=forms.RadioSelect,
        initial="review"
    )
    message = forms.CharField(
        label="Ваше сообщение",
        widget=forms.Textarea()
    )
    rating = forms.ChoiceField(
        choices=[(1, '★'), (2, '★★'), (3, '★★★'), (4, '★★★★'), (5, '★★★★★')],
        label="Оценка",
        required=False,
        widget=forms.RadioSelect(attrs={'class':'form-control'})
    )

CHOICE_PHONE = [
    ("site","Оставить на сайте"),
    ("call","Позвонить"),
]

class ProductForm(forms.Form):
    name = forms.CharField(
        label="Ваше Имя",
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    numTel = forms.CharField(
        label='Номер телефона',
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    adress = forms.CharField(
        label='Адрес',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    langs = forms.ChoiceField(
        choices = CHOICE_PHONE,
        label="Тип обращения",
        widget=forms.RadioSelect,
        initial="call"
    )

class PokupkaForm(forms.ModelForm):
    class Meta:
        model = Pokupka
        fields = ['product_name', 'quantity', 'price', 'customer_name', 
                 'phone', 'delivery_address', 'by_models_order']
        widgets = {
            'product_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: Столешница 2.4м'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'value': 1
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'customer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ваше имя'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 (999) 123-45-67'
            }),
            'delivery_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Адрес доставки'
            }),
            'by_models_order': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'product_name': 'Название товара',
            'quantity': 'Количество',
            'price': 'Цена (₽)',
            'customer_name': 'Имя покупателя',
            'phone': 'Телефон',
            'delivery_address': 'Адрес доставки',
            'by_models_order': 'Связать с заказом (необязательно)',
        }

