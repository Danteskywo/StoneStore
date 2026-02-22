from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q, Avg, Count
from datetime import datetime
from django.views.decorators.http import require_POST

from .forms import UserForm, CountertopOrderForm
from .models import Feedback, Stone, StoneCategory, CountertopOrder

def index(request):
    """Главная страница"""
    popular_stones = Stone.objects.filter(is_popular=True, in_stock=True)[:6]
    new_stones = Stone.objects.filter(is_new=True, in_stock=True)[:4]
    categories = StoneCategory.objects.all()
    recent_reviews = Feedback.objects.filter(request_type='review', is_published=True)[:3]
    
    context = {
        'popular_stones': popular_stones,
        'new_stones': new_stones,
        'categories': categories,
        'recent_reviews': recent_reviews,
        'my_date': datetime.now(),
    }
    return render(request, "index.html", context)

def catalog(request):
    """Каталог камней"""
    category_slug = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    hardness = request.GET.get('hardness')
    search = request.GET.get('search')
    sort = request.GET.get('sort', '-created_at')
    
    stones = Stone.objects.filter(in_stock=True)
    
    if category_slug:
        stones = stones.filter(category__slug=category_slug)
    
    if min_price:
        stones = stones.filter(price_per_sqm__gte=min_price)
    
    if max_price:
        stones = stones.filter(price_per_sqm__lte=max_price)
    
    if hardness:
        stones = stones.filter(hardness__gte=hardness)
    
    if search:
        stones = stones.filter(
            Q(name__icontains=search) | 
            Q(description__icontains=search)
        )
    
    if sort == 'price_asc':
        stones = stones.order_by('price_per_sqm')
    elif sort == 'price_desc':
        stones = stones.order_by('-price_per_sqm')
    elif sort == 'name_asc':
        stones = stones.order_by('name')
    elif sort == 'popular':
        stones = stones.annotate(order_count=Count('countertoporder')).order_by('-order_count')
    else:
        stones = stones.order_by('-created_at')
    
    paginator = Paginator(stones, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = StoneCategory.objects.all()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'current_category': category_slug,
        'min_price': min_price,
        'max_price': max_price,
        'hardness': hardness,
        'search': search,
        'sort': sort,
    }
    return render(request, "catalog.html", context)

def stone_detail(request, slug):
    """Детальная страница камня"""
    stone = get_object_or_404(Stone, slug=slug, in_stock=True)
    
    similar_stones = Stone.objects.filter(
        category=stone.category, 
        in_stock=True
    ).exclude(id=stone.id)[:4]
    
    if request.method == 'POST':
        form = CountertopOrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.stone = stone
            order.save()
            messages.success(request, f'Спасибо, {order.customer_name}! Ваш заказ принят. Наш менеджер свяжется с вами в ближайшее время.')
            return redirect('order_success', order_id=order.id)
    else:
        form = CountertopOrderForm(initial={'stone': stone})
        form.fields['stone'].widget = forms.HiddenInput()
    
    context = {
        'stone': stone,
        'similar_stones': similar_stones,
        'form': form,
    }
    return render(request, "stone_detail.html", context)

def order_success(request, order_id):
    """Страница успешного заказа"""
    order = get_object_or_404(CountertopOrder, id=order_id)
    context = {
        'order': order,
        'area': order.calculate_area(),
        'price': order.calculate_price(),
    }
    return render(request, "order_success.html", context)

def by_product(request):
    """Быстрый заказ столешницы"""
    if request.method == "POST":
        form = CountertopOrderForm(request.POST)
        if form.is_valid():
            order = form.save()
            messages.success(request, f'Спасибо, {order.customer_name}! Ваш заказ принят.')
            return redirect('order_success', order_id=order.id)
    else:
        form = CountertopOrderForm()
    
    stones = Stone.objects.filter(in_stock=True)
    
    context = {
        'form': form,
        'stones': stones,
    }
    return render(request, "by_product.html", context)

def questions(request):
    """Страница отзывов и вопросов"""
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
                request_type=langs,
                name=name,
                numTel=numTel,
                adress=adress,
                message=message,
                rating=rating,
            )

            messages.success(request, f'Спасибо, {name}! Ваше обращение принято.')
            return redirect('questions')
    else:
        form = UserForm()

    filter_type = request.GET.get('type', 'all')
    filter_rating = request.GET.get('rating', 'all')
    search_query = request.GET.get('search', '')

    feedbacks = Feedback.objects.filter(is_published=True)

    if filter_type != 'all':
        feedbacks = feedbacks.filter(request_type=filter_type)
    
    if filter_rating != 'all' and filter_rating.isdigit():
        feedbacks = feedbacks.filter(rating=int(filter_rating))
    
    if search_query:
        feedbacks = feedbacks.filter(
            Q(name__icontains=search_query) |
            Q(message__icontains=search_query)
        )
    
    feedbacks = feedbacks.order_by('-created_at')
    
    total_count = Feedback.objects.count()
    avg_result = Feedback.objects.filter(
        request_type='review',
        rating__isnull=False
    ).aggregate(Avg('rating'))
    avg_rating = avg_result['rating__avg']

    paginator = Paginator(feedbacks, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'form': form,
        'page_obj': page_obj,
        'filter_type': filter_type,
        'filter_rating': filter_rating,
        'search_query': search_query,
        'total_count': total_count,
        'avg_rating': avg_rating,
    }
    return render(request, "questions.html", context)

def gallery(request):
    """Галерея работ"""
    stones = Stone.objects.filter(in_stock=True)
    
    category_id = request.GET.get('category')
    if category_id:
        stones = stones.filter(category_id=category_id)
    
    categories = StoneCategory.objects.all()
    
    context = {
        'stones': stones,
        'categories': categories,
    }
    return render(request, "gallery.html", context)

def about(request):
    """Страница о нас"""
    return render(request, "about.html")

def contact(request):
    """Страница контактов"""
    return render(request, "contact.html")

@require_POST
def calculate_price(request):
    """API для расчета цены"""
    stone_id = request.POST.get('stone_id')
    length = float(request.POST.get('length', 0))
    width = float(request.POST.get('width', 0))
    
    try:
        stone = Stone.objects.get(id=stone_id)
        area = length * width
        price = area * float(stone.price_per_sqm)
        
        return JsonResponse({
            'success': True,
            'area': round(area, 2),
            'price': round(price, 2),
            'price_per_sqm': float(stone.price_per_sqm)
        })
    except (Stone.DoesNotExist, ValueError, TypeError):
        return JsonResponse({'success': False, 'error': 'Ошибка расчета'})