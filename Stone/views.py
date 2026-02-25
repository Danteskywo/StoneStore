from django.shortcuts import render, redirect, get_object_or_404

from django.http import HttpResponse, HttpResponseNotFound, HttpResponseForbidden, HttpResponseBadRequest, JsonResponse

from django.core.paginator import Paginator
from django.core.serializers.json import DjangoJSONEncoder

from django.template.response import TemplateResponse

from django.contrib import messages

from django.db.models import Q, Avg, Sum, Count
from datetime import datetime, timedelta

from .forms import UserForm, ProductForm, PokupkaForm
from .models import Feedback, ByModels, Pokupka

def index(request):
    header = "Данные пользователя"
    langs = ["Python", "JS", "Django", "FastAPI"]
    user = {"name":"Ilya", "age":33}
    host = request.META.get('HTTP_HOST', 'неизвестный хост')
    method = request.method
    path = request.path
    user_agent = request.META.get('HTTP_USER_AGENT', 'неизвестный браузер')
    ip = request.META.get('REMOTE_ADDR', 'неизвестный IP')
    context = {
        "header": header,
        "langs": langs,
        "name": user["name"], 
        "age": user["age"],
        "host": host,
        "method":method,
        "user_agent":user_agent,
        "ip":ip,
        "path":path,
        "my_date": datetime.now()}
    return render (request, "index.html", context=context)
#     return HttpResponse(f'''
#     <p>Host: {host}</p>
#     <p>Path: {path}</p>
#     <p>User_agent:{user_agent}</p>
#     <p>IP:{ip}</p>
#     <p>Method:{method}</p>
# ''')

def by_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            ByModels.objects.create(
            name=form.cleaned_data['name'],
            numTel=form.cleaned_data['numTel'],
            adress=form.cleaned_data['adress'] or "Самовывоз",
            request_by=form.cleaned_data['langs']
            )
            context = {
                'name':form.cleaned_data['name'],
                'numTel':form.cleaned_data['numTel'],
                'adress':form.cleaned_data['adress'] or 'Самовывоз',
                'langs':form.cleaned_data['langs'],
            }
            return render(request, "order_success.html", context)
        else:
            return render(request, "by_product.html",{'form':form})
    else:
        form = ProductForm()
        return render(request,"by_product.html", {'form':form})

def galerey(request):
    return render(request, "galerey.html")

def gallery(request):
    return render(request, "gallery.html")

def about(request):
    return render (request, "about.html" )

def contact(request):
    return render (request,"contact.html" )

def products(request, id):
    return HttpResponse(f"Виды изделий:{id}")

def comments(request, id):
    return HttpResponse(f"Комментарии:{id}")

def questions(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            langs = form.cleaned_data['langs']
            name = form.cleaned_data['name']
            numTel = form.cleaned_data['numTel']
            adress = form.cleaned_data['adress']
            message = form.cleaned_data['message']
            rating = form.cleaned_data.get('rating')

            Feedback.objects.create(
                request_type = langs,
                name = name,
                numTel = numTel,
                adress = adress,
                message = message,
                rating = rating,
            )

            context = {
                'form': form,
                'submitted': True,
                'langs': langs,
                'name': name,
                'numTel': numTel,
                'adress': adress,
                'message': message,
                'rating': rating,
            }
            messages.success(request, f'Спасибо, {name}! Ваше обращение принято.')
            return render(request,"questions.html", context)
    else:
        form = UserForm()

    filter_type = request.GET.get('type','all')
    filter_rating = request.GET.get('rating','all')
    sort_by = request.GET.get('sort','-created_at')
    search_query = request.GET.get('search','')

    feedbacks = Feedback.objects.all()

    if filter_type != 'all':
        feedbacks = feedbacks.filter(request_type=filter_type)
    
    if filter_rating != 'all' and filter_rating.isdigit():  
        feedbacks = feedbacks.filter(rating=int(filter_rating))
    
    if search_query:
        feedbacks = feedbacks.filter(
            Q(name__icontains=search_query) |
            Q(message__icontains=search_query)  
        )
    
    if sort_by == 'rating_asc':
        feedbacks = feedbacks.order_by('rating')
    elif sort_by == 'rating_desc':
        feedbacks = feedbacks.order_by('-rating')
    elif sort_by == 'name_asc':
        feedbacks = feedbacks.order_by('name')
    elif sort_by == 'name_desc':
        feedbacks = feedbacks.order_by('-name')
    elif sort_by == 'oldest':
        feedbacks = feedbacks.order_by('created_at')
    else:
        feedbacks = feedbacks.order_by('-created_at')
    

    total_count = Feedback.objects.count()

    avg_result = Feedback.objects.filter(
        request_type='review',
        rating__isnull=False
    ).aggregate(Avg('rating'))
    avg_rating = avg_result['rating__avg']


# ПАГИНАЦИЯ

    paginator = Paginator(feedbacks, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'form': form,
        'submitted': False,
        'page_obj': page_obj,
        'feedbacks': page_obj,
        'filter_type': filter_type,
        'filter_rating': filter_rating,
        'sort_by': sort_by,
        'search_query': search_query,
        'total_count': total_count,
        'avg_rating': avg_rating,
    }

    return render (request, "questions.html", context)

def new(request):
    return HttpResponse("New")

def top(request):
    return HttpResponse("Top")

def user(request):
    name = request.GET.get("name", "Неопределено")
    age = request.GET.get("age", 0)
    return HttpResponse(f"<h2>Имя:{name} Возраст:{age}</h2>")

def pokupka_list(request):
    pokupki = Pokupka.objects.all()
    status_filter = request.GET.get('status','all')
    if status_filter != 'all':
        pokupki = pokupki.filter(status=status_filter)

    search_query = request.GET.get('search','')
    if search_query:
        pokupki = pokupki.filter(
            Q(product_name__icontains=search_query)|
            Q(customer_name__icontains=search_query)
        )

    date_filter = request.GET.get('date','all')
    if date_filter == 'week':
        week_go = datetime.now() - timedelta(days=7)
        pokupki = pokupki.filter(created_at__gte=week_go)
    elif date_filter == "month":
        month_ago = datetime.now() - timedelta(days=30)
        pokupki = pokupki.filter(created_at__gte=month_ago)

    total_count = pokupki.count()
    total_sum = pokupki.aggregate(total=Sum('price'))['total'] or 0
    avg_price = pokupki.aggregate(avg=Avg('price'))['avg'] or 0

    paginator = Paginator(pokupki, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'total_count': total_count,
        'total_sum': total_sum,
        'avg_price': avg_price,
        'current_status': status_filter,
        'search_query': search_query,
        'date_filter': date_filter,
    }
    return render (request, 'pokupka_list.html', context)
    
def create_pokupka(request):
    if request.method == 'POST':
        form = PokupkaForm(request.POST)
        if form.is_valid():
            pokupka = form.save()
            messages.success(request, f'Покупка "{pokupka.product_name}" успешно создана!')
            return redirect('pokupka_list')
        # Если форма не валидна, показываем форму с ошибками
    else:
        # GET запрос - создаем пустую форму
        form = PokupkaForm()
    
    # Для обоих случаев (GET и невалидный POST) настраиваем queryset и рендерим шаблон
    form.fields['by_models_order'].queryset = ByModels.objects.all().order_by('-created_at')
    return render(request, 'create_pokupka.html', {'form': form})

def pokupka_detail(request, pk):
    pokupka = get_object_or_404(Pokupka, pk=pk)
    return render (request, 'pokupka_detail.html', {'pokupka':pokupka})
        


############################
class Person:
    def __init__(self, name, age):
        self.name = name 
        self.age = age
class PersonEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Person):
            return {"name":obj.name, "age":obj.age}
        return super().default(obj)

def user_response(request):
    ilya = Person("Ilya", 33)
    return JsonResponse (ilya, safe=False, encoder=PersonEncoder)
#################################