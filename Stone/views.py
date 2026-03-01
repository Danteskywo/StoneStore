from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q, Avg, Count, Sum
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.core.cache import cache
from django.utils import timezone
from django import forms
from datetime import datetime, timedelta
from .models import Stone, StoneCategory, CountertopOrder, Feedback, Wishlist, Comparison
from .forms import UserForm, ProductForm, UserRegistrationForm, UserProfileForm
from calculator.calculator_core import StoneCalculator
from calculator.models import SavedCalculation
from notifications.telegram_bot import TelegramNotifier
from django.db import transaction
import json
import logging

logger = logging.getLogger(__name__)

@cache_page(60 * 15)
@vary_on_cookie
def index(request):
    try:
        popular_stones = Stone.objects.filter(is_popular=True, in_stock=True)[:6]
        new_stones = Stone.objects.filter(is_new=True, in_stock=True)[:4]
        categories = StoneCategory.objects.all()
        recent_reviews = Feedback.objects.filter(
            request_type='review', 
            is_published=True, 
            moderation_status='approved'
        )[:3]
        
        context = {
            'popular_stones': popular_stones,
            'new_stones': new_stones,
            'categories': categories,
            'recent_reviews': recent_reviews,
            'my_date': datetime.now(),
        }
        return render(request, "index.html", context)
    except Exception as e:
        logger.error(f"Error in index view: {e}")
        return render(request, "index.html", {'error': 'Произошла ошибка при загрузке страницы'})

def catalog(request):
    try:
        category_slug = request.GET.get('category')
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        hardness = request.GET.get('hardness')
        search = request.GET.get('search')
        sort = request.GET.get('sort', '-created_at')
        page = int(request.GET.get('page', 1))
        
        stones = Stone.objects.filter(in_stock=True).select_related('category')
        
        if category_slug:
            stones = stones.filter(category__slug=category_slug)
        
        if min_price:
            try:
                stones = stones.filter(price_per_sqm__gte=float(min_price))
            except ValueError:
                pass
        
        if max_price:
            try:
                stones = stones.filter(price_per_sqm__lte=float(max_price))
            except ValueError:
                pass
        
        if hardness:
            try:
                stones = stones.filter(hardness__gte=int(hardness))
            except ValueError:
                pass
        
        if search:
            stones = stones.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search) |
                Q(category__name__icontains=search)
            )
        
        if sort == 'price_asc':
            stones = stones.order_by('price_per_sqm')
        elif sort == 'price_desc':
            stones = stones.order_by('-price_per_sqm')
        elif sort == 'name_asc':
            stones = stones.order_by('name')
        elif sort == 'popular':
            stones = stones.annotate(
                order_count=Count('countertoporder')
            ).order_by('-order_count', '-created_at')
        else:
            stones = stones.order_by('-created_at')
        
        paginator = Paginator(stones, 12)
        page_obj = paginator.get_page(page)
        
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
    except Exception as e:
        logger.error(f"Error in catalog view: {e}")
        messages.error(request, 'Произошла ошибка при загрузке каталога')
        return render(request, "catalog.html", {'page_obj': None})

def stone_detail(request, slug):
    try:
        stone = get_object_or_404(Stone, slug=slug, in_stock=True)
        
        cache_key = f'similar_stones_{slug}'
        similar_stones = cache.get(cache_key)
        
        if similar_stones is None:
            similar_stones = Stone.objects.filter(
                category=stone.category, 
                in_stock=True
            ).exclude(id=stone.id)[:4]
            cache.set(cache_key, similar_stones, 60 * 60)
        
        in_wishlist = False
        if request.user.is_authenticated:
            in_wishlist = Wishlist.objects.filter(user=request.user, stone=stone).exists()
        
        if request.method == 'POST':
            form = ProductForm(request.POST)
            if form.is_valid():
                order = form.save(commit=False)
                order.stone = stone
                order.save()
                
                try:
                    telegram = TelegramNotifier()
                    telegram.send_order_notification(order)
                except Exception as e:
                    logger.error(f"Telegram notification error: {e}")
                
                messages.success(request, f'Спасибо, {order.customer_name}! Ваш заказ принят.')
                return redirect('order_success', order_id=order.id)
        else:
            initial = {}
            if request.GET.get('length'):
                initial['length'] = request.GET.get('length')
            if request.GET.get('width'):
                initial['width'] = request.GET.get('width')
            if request.GET.get('thickness'):
                initial['thickness'] = request.GET.get('thickness')
            
            form = ProductForm(initial=initial)
            form.fields['stone'].widget = forms.HiddenInput()
            form.fields['stone'].initial = stone.id
        
        context = {
            'stone': stone,
            'similar_stones': similar_stones,
            'form': form,
            'in_wishlist': in_wishlist,
        }
        return render(request, "stone_detail.html", context)
    except Exception as e:
        logger.error(f"Error in stone_detail view: {e}")
        messages.error(request, 'Произошла ошибка при загрузке страницы')
        return redirect('catalog')

def order_success(request, order_id):
    try:
        order = get_object_or_404(CountertopOrder, id=order_id)
        context = {
            'order': order,
            'area': order.calculate_area(),
            'price': order.calculate_price(),
        }
        return render(request, "order_success.html", context)
    except Exception as e:
        logger.error(f"Error in order_success view: {e}")
        messages.error(request, 'Заказ не найден')
        return redirect('catalog')

def by_product(request):
    try:
        if request.method == "POST":
            form = ProductForm(request.POST)
            if form.is_valid():
                with transaction.atomic():
                    order = form.save()
                    
                    promo = request.session.get('applied_promo')
                    if promo:
                        order.promo_code = promo['code']
                        order.discount_amount = promo['discount']
                        order.save()
                        del request.session['applied_promo']
                    
                    try:
                        telegram = TelegramNotifier()
                        telegram.send_order_notification(order)
                    except Exception as e:
                        logger.error(f"Telegram notification error: {e}")
                    
                    messages.success(request, f'Спасибо, {order.customer_name}! Ваш заказ принят.')
                    return redirect('order_success', order_id=order.id)
        else:
            initial = {}
            stone_id = request.GET.get('stone')
            if stone_id:
                initial['stone'] = stone_id
            
            for param in ['length', 'width', 'thickness', 'edge_type']:
                value = request.GET.get(param)
                if value:
                    initial[param] = value
            
            has_sink = request.GET.get('has_sink')
            if has_sink == '1':
                initial['sink_type'] = 'undermount'
            
            form = ProductForm(initial=initial)
        
        stones = Stone.objects.filter(in_stock=True)
        
        context = {
            'form': form,
            'stones': stones,
        }
        return render(request, "by_product.html", context)
    except Exception as e:
        logger.error(f"Error in by_product view: {e}")
        messages.error(request, 'Произошла ошибка при обработке заказа')
        return redirect('catalog')

def questions(request):
    try:
        if request.method == "POST":
            form = UserForm(request.POST, request.FILES)
            if form.is_valid():
                with transaction.atomic():
                    feedback = Feedback.objects.create(
                        request_type=form.cleaned_data['langs'],
                        name=form.cleaned_data['name'],
                        numTel=form.cleaned_data['numTel'],
                        adress=form.cleaned_data['adress'],
                        message=form.cleaned_data['message'],
                        rating=form.cleaned_data.get('rating'),
                        image1=form.cleaned_data.get('image1'),
                        image2=form.cleaned_data.get('image2'),
                        image3=form.cleaned_data.get('image3'),
                    )
                    
                    try:
                        telegram = TelegramNotifier()
                        telegram.send_feedback_notification(feedback)
                    except Exception as e:
                        logger.error(f"Telegram notification error: {e}")
                    
                    messages.success(request, f'Спасибо, {feedback.name}! Ваше обращение принято.')
                    return redirect('questions')
        else:
            form = UserForm()

        filter_type = request.GET.get('type', 'all')
        filter_rating = request.GET.get('rating', 'all')
        search_query = request.GET.get('search', '')
        page = int(request.GET.get('page', 1))

        feedbacks = Feedback.objects.filter(is_published=True, moderation_status='approved')

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
            rating__isnull=False,
            is_published=True,
            moderation_status='approved'
        ).aggregate(Avg('rating'))
        avg_rating = avg_result['rating__avg']

        paginator = Paginator(feedbacks, 10)
        page_obj = paginator.get_page(page)

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
    except Exception as e:
        logger.error(f"Error in questions view: {e}")
        messages.error(request, 'Произошла ошибка при загрузке страницы')
        return render(request, "questions.html", {'form': UserForm()})

def gallery(request):
    try:
        stones = Stone.objects.filter(in_stock=True).prefetch_related('images')
        category_id = request.GET.get('category')
        
        if category_id:
            stones = stones.filter(category_id=category_id)
        
        categories = StoneCategory.objects.all()
        
        context = {
            'stones': stones,
            'categories': categories,
        }
        return render(request, "gallery.html", context)
    except Exception as e:
        logger.error(f"Error in gallery view: {e}")
        return render(request, "gallery.html", {'error': 'Ошибка загрузки галереи'})

def about(request):
    return render(request, "about.html")

def contact(request):
    return render(request, "contact.html")

@login_required
def add_to_wishlist(request, stone_id):
    """Добавление в избранное"""
    if request.method == 'POST':
        try:
            stone = Stone.objects.get(id=stone_id)
            
            # Проверяем есть ли уже
            exists = Wishlist.objects.filter(user=request.user, stone=stone).exists()
            
            if exists:
                Wishlist.objects.filter(user=request.user, stone=stone).delete()
                return JsonResponse({'success': True, 'action': 'removed'})
            else:
                Wishlist.objects.create(user=request.user, stone=stone)
                return JsonResponse({'success': True, 'action': 'added'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False})

@login_required
def wishlist_view(request):
    """Страница избранного"""
    try:
        # Получаем все товары из избранного для текущего пользователя
        wishlist_items = Wishlist.objects.filter(
            user=request.user
        ).select_related('stone', 'stone__category')
        
        # Просто передаем их в шаблон
        context = {
            'wishlist_items': wishlist_items
        }
        return render(request, 'wishlist.html', context)
        
    except Exception as e:
        # Логируем ошибку
        print(f"Ошибка в wishlist_view: {e}")
        # Показываем сообщение об ошибке
        messages.error(request, 'Ошибка загрузки избранного')
        return render(request, 'wishlist.html', {'wishlist_items': []})

@login_required
def check_wishlist_status(request, stone_id):
    try:
        in_wishlist = Wishlist.objects.filter(
            user=request.user, 
            stone_id=stone_id
        ).exists()
        return JsonResponse({'in_wishlist': in_wishlist})
    except Exception as e:
        logger.error(f"Error in check_wishlist_status: {e}")
        return JsonResponse({'in_wishlist': False})

def add_to_comparison(request, stone_id):
    """Добавление в сравнение"""
    if request.method == 'POST':
        try:
            stone = Stone.objects.get(id=stone_id)
            
            # Создаем сессию если нет
            if not request.session.session_key:
                request.session.create()
            
            # Получаем или создаем сравнение
            comparison, created = Comparison.objects.get_or_create(
                session_key=request.session.session_key
            )
            
            # Проверяем есть ли уже
            if comparison.stones.filter(id=stone_id).exists():
                comparison.stones.remove(stone)
                return JsonResponse({'success': True, 'action': 'removed', 'count': comparison.stones.count()})
            else:
                if comparison.stones.count() >= 4:
                    return JsonResponse({'success': False, 'error': 'Максимум 4 камня'})
                
                comparison.stones.add(stone)
                return JsonResponse({'success': True, 'action': 'added', 'count': comparison.stones.count()})
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False})

def comparison_view(request):
    """Страница сравнения"""
    try:
        session_key = request.session.session_key
        stones = []
        
        if session_key:
            comparison = Comparison.objects.filter(session_key=session_key).first()
            if comparison:
                stones = comparison.stones.all().select_related('category')
        
        characteristics = []
        if stones:
            char_titles = {
                'price': 'Цена (₽/м²)',
                'hardness': 'Твердость (1-10)',
                'water_absorption': 'Водопоглощение (%)',
                'frost_resistance': 'Морозостойкость',
            }
            
            for char_key, char_title in char_titles.items():
                row = {
                    'title': char_title,
                    'values': []
                }
                
                for stone in stones:
                    if char_key == 'price':
                        value = f"{stone.price_per_sqm} ₽"
                    elif char_key == 'hardness':
                        value = f"{stone.hardness}/10"
                    elif char_key == 'water_absorption':
                        value = f"{stone.water_absorption}%"
                    elif char_key == 'frost_resistance':
                        value = 'Да' if stone.frost_resistance else 'Нет'
                    else:
                        value = '—'
                    
                    row['values'].append(value)
                
                characteristics.append(row)
        
        context = {
            'stones': stones,
            'characteristics': characteristics
        }
        return render(request, 'comparison.html', context)
        
    except Exception as e:
        print(f"Error in comparison_view: {e}")
        return render(request, 'comparison.html', {'stones': [], 'error': 'Ошибка загрузки сравнения'})

def remove_from_comparison(request, stone_id):
    """Удаление из сравнения"""
    if request.method == 'POST':
        try:
            session_key = request.session.session_key
            if not session_key:
                return JsonResponse({'success': False, 'error': 'Сессия не найдена'})
            
            comparison = Comparison.objects.filter(session_key=session_key).first()
            if not comparison:
                return JsonResponse({'success': False, 'error': 'Сравнение не найдено'})
            
            stone = Stone.objects.get(id=stone_id)
            comparison.stones.remove(stone)
            
            return JsonResponse({
                'success': True,
                'count': comparison.stones.count()
            })
            
        except Stone.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Камень не найден'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Только POST запросы'})

def register(request):
    try:
        if request.method == 'POST':
            form = UserRegistrationForm(request.POST)
            if form.is_valid():
                user = form.save()
                login(request, user)
                messages.success(request, 'Регистрация прошла успешно!')
                return redirect('profile')
        else:
            form = UserRegistrationForm()
        
        return render(request, 'registration/register.html', {'form': form})
    except Exception as e:
        logger.error(f"Error in register view: {e}")
        messages.error(request, 'Ошибка при регистрации')
        return redirect('home')

@login_required
def profile(request):
    try:
        user = request.user
        orders = CountertopOrder.objects.filter(
            customer_phone=user.phone
        ).select_related('stone').order_by('-created_at')[:5]
        
        calculations = SavedCalculation.objects.filter(
            user=user
        ).select_related('stone').order_by('-created_at')[:5]
        
        wishlist = Wishlist.objects.filter(
            user=user
        ).select_related('stone')[:5]
        
        context = {
            'user': user,
            'orders': orders,
            'calculations': calculations,
            'wishlist': wishlist
        }
        return render(request, 'profile/profile.html', context)
    except Exception as e:
        logger.error(f"Error in profile view: {e}")
        return render(request, 'profile/profile.html', {'error': 'Ошибка загрузки профиля'})

@login_required
def profile_edit(request):
    try:
        if request.method == 'POST':
            form = UserProfileForm(request.POST, request.FILES, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, 'Профиль обновлен')
                return redirect('profile')
        else:
            form = UserProfileForm(instance=request.user)
        
        return render(request, 'profile/edit.html', {'form': form})
    except Exception as e:
        logger.error(f"Error in profile_edit view: {e}")
        messages.error(request, 'Ошибка при обновлении профиля')
        return redirect('profile')

@login_required
def profile_orders(request):
    try:
        orders = CountertopOrder.objects.filter(
            customer_phone=request.user.phone
        ).select_related('stone').order_by('-created_at')
        
        return render(request, 'profile/orders.html', {'orders': orders})
    except Exception as e:
        logger.error(f"Error in profile_orders view: {e}")
        return render(request, 'profile/orders.html', {'error': 'Ошибка загрузки заказов'})

@login_required
def profile_calculations(request):
    try:
        calculations = SavedCalculation.objects.filter(
            user=request.user
        ).select_related('stone').order_by('-created_at')
        
        return render(request, 'profile/calculations.html', {'calculations': calculations})
    except Exception as e:
        logger.error(f"Error in profile_calculations view: {e}")
        return render(request, 'profile/calculations.html', {'error': 'Ошибка загрузки расчетов'})

def login_view(request):
    try:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', 'profile')
                messages.success(request, f'Добро пожаловать, {user.username}!')
                return redirect(next_url)
            else:
                messages.error(request, 'Неверное имя пользователя или пароль')
        
        return render(request, 'registration/login.html')
    except Exception as e:
        logger.error(f"Error in login_view: {e}")
        messages.error(request, 'Ошибка при входе')
        return render(request, 'registration/login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы')
    return redirect('home')