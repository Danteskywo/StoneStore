from django import forms

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

