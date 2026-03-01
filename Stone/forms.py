from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import Feedback, CountertopOrder, Stone
import re

User = get_user_model()

class PhoneInput(forms.TextInput):
    def __init__(self, attrs=None):
        default_attrs = {
            'type': 'tel',
            'placeholder': '+7 (___) ___-__-__',
            'class': 'form-control phone-mask',
            'pattern': '\\+7\\s?\\(?\\d{3}\\)?\\s?\\d{3}-?\\d{2}-?\\d{2}',
            'maxlength': '18'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)

class PhoneField(forms.CharField):
    def __init__(self, **kwargs):
        kwargs.setdefault('widget', PhoneInput())
        kwargs.setdefault('max_length', 18)
        kwargs.setdefault('min_length', 18)
        kwargs.setdefault('required', True)
        kwargs.setdefault('error_messages', {
            'required': 'Номер телефона обязателен',
            'min_length': 'Номер должен содержать 11 цифр',
            'max_length': 'Номер должен содержать 11 цифр',
        })
        super().__init__(**kwargs)
    
    def clean(self, value):
        value = super().clean(value)
        if not value:
            return value
            
        # Очищаем от лишних символов
        digits = re.sub(r'\D', '', value)
        
        # Проверка формата
        if not value.startswith('+7') and not value.startswith('8'):
            raise forms.ValidationError('Номер должен начинаться с +7 или 8')
        
        if len(digits) != 11:
            raise forms.ValidationError('Номер должен содержать 11 цифр')
        
        # Приводим к единому формату
        if digits.startswith('8'):
            digits = '7' + digits[1:]
        formatted = f"+7 ({digits[1:4]}) {digits[4:7]}-{digits[7:9]}-{digits[9:11]}"
        
        return formatted

CHOICE_TYPE = [
    ("review", "Отзыв"),
    ("question", "Вопрос"),
]

class UserForm(forms.Form):
    langs = forms.ChoiceField(
        choices=CHOICE_TYPE,
        label="Тип обращения",
        widget=forms.RadioSelect(attrs={'class': 'radio-group'}),
        initial="review"
    )
    
    name = forms.CharField(
        label="Ваше Имя",
        max_length=30,
        min_length=2,
        error_messages={
            'required': 'Имя обязательно для заполнения',
            'min_length': 'Имя должно содержать минимум 2 символа',
        },
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Иван Петров'
        })
    )
    
    numTel = PhoneField(label='Номер телефона')
    
    rating = forms.ChoiceField(
        choices=[(5, '★★★★★'), (4, '★★★★'), (3, '★★★'), (2, '★★'), (1, '★')],
        label="Оценка",
        required=False,
        widget=forms.RadioSelect(attrs={'class': 'star-rating'})
    )
    
    message = forms.CharField(
        label="Сообщение",
        min_length=10,
        max_length=2000,
        error_messages={
            'required': 'Сообщение обязательно для заполнения',
            'min_length': 'Сообщение должно содержать минимум 10 символов',
        },
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Напишите ваш отзыв или вопрос...'
        })
    )
    
    adress = forms.CharField(
        label='Адрес (необязательно)',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'г. Москва, ул. Примерная, д. 1'
        })
    )
    
    image1 = forms.ImageField(
        label='Фото работы',
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control-file',
            'accept': 'image/jpeg,image/png,image/gif,image/webp'
        })
    )
    image2 = forms.ImageField(
        label='Дополнительное фото',
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control-file',
            'accept': 'image/jpeg,image/png,image/gif,image/webp'
        })
    )
    image3 = forms.ImageField(
        label='Еще фото',
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control-file',
            'accept': 'image/jpeg,image/png,image/gif,image/webp'
        })
    )
    
    consent = forms.BooleanField(
        label='Я согласен на обработку персональных данных',
        required=True,
        error_messages={
            'required': 'Необходимо согласие на обработку персональных данных'
        },
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        langs = cleaned_data.get('langs')
        rating = cleaned_data.get('rating')
        
        # Для отзывов оценка обязательна
        if langs == 'review' and not rating:
            self.add_error('rating', 'Для отзыва необходимо указать оценку')
        
        return cleaned_data

class ProductForm(forms.ModelForm):
    customer_phone = PhoneField(label='Телефон')
    
    class Meta:
        model = CountertopOrder
        fields = ['stone', 'length', 'width', 'thickness', 'edge_type', 'sink_type', 
                 'cutouts', 'customer_name', 'customer_phone', 'customer_email', 
                 'customer_address', 'comment']
        widgets = {
            'stone': forms.Select(attrs={
                'class': 'form-select form-select-lg'
            }),
            'length': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.5',
                'max': '5',
                'placeholder': '2.0'
            }),
            'width': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.5',
                'max': '3',
                'placeholder': '0.6'
            }),
            'thickness': forms.Select(attrs={
                'class': 'form-select'
            }),
            'edge_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'sink_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'cutouts': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Опишите необходимые вырезы под мойку, плиту и т.д.'
            }),
            'customer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Иванов Иван Иванович'
            }),
            'customer_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'ivan@example.com'
            }),
            'customer_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'г. Москва, ул. Примерная, д. 1, кв. 1'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Дополнительные пожелания по заказу'
            }),
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
            'customer_email': 'Email',
            'customer_address': 'Адрес доставки',
            'comment': 'Комментарий',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем цену к опциям выбора камня
        if 'stone' in self.fields:
            self.fields['stone'].queryset = Stone.objects.filter(in_stock=True)
            self.fields['stone'].label_from_instance = lambda obj: f"{obj.name} - {obj.price_per_sqm} ₽/м²"
    
    def clean(self):
        cleaned_data = super().clean()
        length = cleaned_data.get('length')
        width = cleaned_data.get('width')
        
        if length and width:
            area = float(length) * float(width)
            if area < 0.1:
                self.add_error('length', 'Минимальная площадь заказа - 0.1 м²')
            if area > 15:
                self.add_error('length', 'Максимальная площадь заказа - 15 м²')
        
        return cleaned_data

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        error_messages={
            'required': 'Email обязателен для заполнения',
            'invalid': 'Введите корректный email адрес'
        },
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'ivan@example.com'
        })
    )
    phone = PhoneField(label='Телефон')
    
    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ivan123'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Подтвердите пароль'
        })
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует')
        return email

class UserProfileForm(forms.ModelForm):
    phone = PhoneField(label='Телефон', required=False)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'first_name', 'last_name', 
                 'birth_date', 'address', 'avatar', 'email_notifications', 
                 'sms_notifications')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'readonly': True
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Иван'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Петров'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'ivan@example.com'
            }),
            'birth_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'address': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Ваш адрес'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control-file',
                'accept': 'image/jpeg,image/png,image/gif'
            }),
            'email_notifications': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'sms_notifications': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }