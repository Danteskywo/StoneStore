from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q, Avg, Count, Sum, Prefetch
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.views.decorators.http import require_POST
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from django import forms
from datetime import datetime, timedelta
from .models import Stone, StoneCategory, CountertopOrder, Feedback, Wishlist, Comparison, ContactMessage
from .forms import ContactForm, UserForm, ProductForm, UserRegistrationForm, UserProfileForm
from calculator.calculator_core import StoneCalculator
from calculator.models import SavedCalculation
from notifications.telegram_bot import TelegramNotifier
from django.db import transaction
import json
import logging
import re

logger = logging.getLogger(__name__)

def clean_search_param(value):
    """Очищает поисковый параметр от лишних символов"""
    if not value or value == 'None':
        return ''
    return value.strip()

def clean_price_param(value):
    """Очищает ценовой параметр"""
    if not value or value == 'None':
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def clean_int_param(value):
    """Очищает целочисленный параметр"""
    if not value or value == 'None':
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None

def create_safe_slug(name):
    """Создает безопасный slug из названия"""
    if not name:
        return ''
    # Транслитерация кириллицы в латиницу
    translit_map = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'E',
        'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
        'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
        'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Shch',
        'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya',
    }
    
    result = ''
    for char in name:
        result += translit_map.get(char, char)
    
    # Заменяем пробелы и другие символы на дефисы
    result = re.sub(r'[^\w\s-]', '', result)
    result = re.sub(r'[-\s]+', '-', result)
    return result.strip('-').lower()

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
        # Получаем и очищаем параметры
        category_slug = clean_search_param(request.GET.get('category'))
        min_price = clean_price_param(request.GET.get('min_price'))
        max_price = clean_price_param(request.GET.get('max_price'))
        hardness = clean_int_param(request.GET.get('hardness'))
        search = clean_search_param(request.GET.get('search'))
        sort = request.GET.get('sort', '-created_at')
        page = request.GET.get('page', 1)
        
        # Валидация page
        try:
            page = int(page)
            if page < 1:
                page = 1
        except (ValueError, TypeError):
            page = 1
        
        # Базовый запрос
        stones = Stone.objects.filter(in_stock=True).select_related('category')
        
        # Применяем фильтры
        if category_slug:
            # Пробуем найти по slug
            stones = stones.filter(category__slug=category_slug)
            
            # Если ничего не найдено, пробуем найти по названию
            if not stones.exists():
                stones = Stone.objects.filter(in_stock=True).select_related('category')
                stones = stones.filter(category__name__icontains=category_slug)
        
        if min_price is not None:
            stones = stones.filter(price_per_sqm__gte=min_price)
        
        if max_price is not None:
            stones = stones.filter(price_per_sqm__lte=max_price)
        
        if hardness is not None:
            stones = stones.filter(hardness__gte=hardness)
        
        if search:
            # Сложный поиск по нескольким полям
            stones = stones.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search) |
                Q(category__name__icontains=search) |
                Q(characteristics__icontains=search)
            )
        
        # Применяем сортировку
        if sort == 'price_asc':
            stones = stones.order_by('price_per_sqm')
        elif sort == 'price_desc':
            stones = stones.order_by('-price_per_sqm')
        elif sort == 'name_asc':
            stones = stones.order_by('name')
        elif sort == 'name_desc':
            stones = stones.order_by('-name')
        elif sort == 'hardness_asc':
            stones = stones.order_by('hardness')
        elif sort == 'hardness_desc':
            stones = stones.order_by('-hardness')
        elif sort == 'popular':
            stones = stones.annotate(
                order_count=Count('countertoporder')
            ).order_by('-order_count', '-created_at')
        elif sort == 'new':
            stones = stones.order_by('-created_at')
        else:
            stones = stones.order_by('-created_at')
        
        # Пагинация
        paginator = Paginator(stones, 12)
        
        # Обработка случая, когда запрошенная страница больше максимальной
        if page > paginator.num_pages and paginator.num_pages > 0:
            page = paginator.num_pages
        
        page_obj = paginator.get_page(page)
        
        # Создаем безопасные slug для каждого камня
        for stone in page_obj:
            stone.safe_slug = create_safe_slug(stone.name)
        
        # Получаем все категории для фильтра
        categories = StoneCategory.objects.all().order_by('name')
        
        # Формируем контекст
        context = {
            'page_obj': page_obj,
            'categories': categories,
            'current_category': category_slug,
            'min_price': min_price if min_price is not None else '',
            'max_price': max_price if max_price is not None else '',
            'hardness': hardness if hardness is not None else '',
            'search': search,
            'sort': sort,
            'paginator': paginator,
            'is_paginated': paginator.num_pages > 1,
        }
        
        return render(request, "catalog.html", context)
        
    except Exception as e:
        logger.error(f"Error in catalog view: {e}")
        messages.error(request, 'Произошла ошибка при загрузке каталога')
        return render(request, "catalog.html", {'page_obj': None, 'categories': []})

def stone_detail(request, slug):
    try:
        # Пытаемся найти камень по slug
        stone = get_object_or_404(Stone, slug=slug, in_stock=True)
        
        # Кэшируем похожие товары
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
        
        # Создаем безопасный slug для использования в шаблоне
        stone.safe_slug = create_safe_slug(stone.name)
        
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
    """Страница заказа товара"""
    try:
        # Получаем параметры из GET запроса
        stone_slug = clean_search_param(request.GET.get('stone_slug'))
        stone_id = request.GET.get('stone')
        
        initial = {}
        
        # Если передан slug, находим камень и подставляем его ID
        if stone_slug:
            try:
                # Пробуем найти по оригинальному slug
                stone = Stone.objects.filter(slug=stone_slug, in_stock=True).first()
                
                # Если не нашли, пробуем найти по имени
                if not stone:
                    stones = Stone.objects.filter(in_stock=True)
                    for s in stones:
                        if create_safe_slug(s.name) == stone_slug:
                            stone = s
                            break
                
                if stone:
                    initial['stone'] = stone.id
                else:
                    messages.error(request, 'Камень не найден')
                    return redirect('catalog')
                    
            except Exception as e:
                logger.error(f"Error finding stone by slug: {e}")
                messages.error(request, 'Камень не найден')
                return redirect('catalog')
        elif stone_id:
            initial['stone'] = stone_id
        
        # Добавляем остальные параметры
        for param in ['length', 'width', 'thickness', 'edge_type']:
            value = request.GET.get(param)
            if value:
                initial[param] = value
        
        has_sink = request.GET.get('has_sink')
        if has_sink == '1':
            initial['sink_type'] = 'undermount'
        
        if request.method == "POST":
            form = ProductForm(request.POST)
            if form.is_valid():
                with transaction.atomic():
                    order = form.save()
                    
                    # Применяем промокод из сессии
                    promo = request.session.get('applied_promo')
                    if promo:
                        order.promo_code = promo['code']
                        order.discount_amount = promo['discount']
                        order.save()
                        del request.session['applied_promo']
                    
                    # Отправка уведомления
                    try:
                        telegram = TelegramNotifier()
                        telegram.send_order_notification(order)
                    except Exception as e:
                        logger.error(f"Telegram notification error: {e}")
                    
                    messages.success(request, f'Спасибо, {order.customer_name}! Ваш заказ принят.')
                    return redirect('order_success', order_id=order.id)
        else:
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

@login_required
def questions(request):
    """Страница отзывов и вопросов (только для авторизованных)"""
    try:
        if request.method == "POST":
            form = UserForm(request.POST, request.FILES)
            if form.is_valid():
                with transaction.atomic():
                    parent_id = request.POST.get('parent_id')
                    parent = None
                    if parent_id:
                        try:
                            parent = Feedback.objects.get(id=parent_id)
                        except Feedback.DoesNotExist:
                            pass
                    
                    feedback = Feedback(
                        request_type=form.cleaned_data['langs'],
                        name=form.cleaned_data['name'],
                        numTel=form.cleaned_data['numTel'],
                        adress=form.cleaned_data['adress'],
                        message=form.cleaned_data['message'],
                        rating=form.cleaned_data.get('rating'),
                        image1=form.cleaned_data.get('image1'),
                        image2=form.cleaned_data.get('image2'),
                        image3=form.cleaned_data.get('image3'),
                        parent=parent
                    )
                    
                    # Сохраняем с указанием пользователя для авто-модерации
                    feedback.save_with_user(request.user)
                    
                    try:
                        telegram = TelegramNotifier()
                        telegram.send_feedback_notification(feedback)
                    except Exception as e:
                        logger.error(f"Telegram notification error: {e}")
                    
                    messages.success(request, f'Спасибо, {feedback.name}! Ваше обращение принято.')
                    return redirect('questions')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
        else:
            form = UserForm()

        filter_type = request.GET.get('type', 'all')
        filter_rating = request.GET.get('rating', 'all')
        search_query = request.GET.get('search', '')
        page = int(request.GET.get('page', 1))

        # Получаем все одобренные отзывы и ответы на них
        feedbacks = Feedback.objects.filter(
            moderation_status='approved',
            is_published=True,
            parent__isnull=True  # Только родительские сообщения (не ответы)
        ).select_related('user').prefetch_related(
            Prefetch('replies', queryset=Feedback.objects.filter(
                moderation_status='approved', 
                is_published=True
            ).select_related('user'))
        )

        if filter_type != 'all':
            feedbacks = feedbacks.filter(request_type=filter_type)
        
        if filter_rating != 'all' and filter_rating.isdigit():
            feedbacks = feedbacks.filter(rating=int(filter_rating))
        
        if search_query:
            feedbacks = feedbacks.filter(
                Q(name__icontains=search_query) |
                Q(message__icontains=search_query)
            )
        
        # Сортируем по дате
        feedbacks = feedbacks.order_by('-created_at')
        
        # Статистика
        total_count = Feedback.objects.count()
        avg_result = Feedback.objects.filter(
            request_type='review',
            rating__isnull=False,
            moderation_status='approved',
            is_published=True
        ).aggregate(Avg('rating'))
        avg_rating = avg_result['rating__avg']

        paginator = Paginator(feedbacks, 10)
        page_obj = paginator.get_page(page)

        # Для каждого отзыва проверяем, может ли пользователь его удалить
        for feedback in page_obj:
            feedback.can_delete_flag = feedback.can_delete(request.user)
            for reply in feedback.replies.all():
                reply.can_delete_flag = reply.can_delete(request.user)

        context = {
            'form': form,
            'page_obj': page_obj,
            'filter_type': filter_type,
            'filter_rating': filter_rating,
            'search_query': search_query,
            'total_count': total_count,
            'avg_rating': avg_rating,
            'user': request.user,
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
    """Страница контактов"""
    try:
        if request.method == 'POST':
            form = ContactForm(request.POST)
            if form.is_valid():
                name = form.cleaned_data['name']
                email = form.cleaned_data['email']
                message = form.cleaned_data['message']
                
                # Сохраняем в базу данных
                contact_message = ContactMessage.objects.create(
                    name=name,
                    email=email,
                    message=message
                )
                
                # Отправляем уведомление на email администратора
                try:
                    send_mail(
                        f'Новое сообщение от {name}',
                        f'Имя: {name}\nEmail: {email}\n\nСообщение:\n{message}',
                        settings.DEFAULT_FROM_EMAIL,
                        [settings.DEFAULT_FROM_EMAIL],
                        fail_silently=True
                    )
                except Exception as e:
                    logger.error(f"Error sending email: {e}")
                
                # Отправляем уведомление в Telegram
                try:
                    telegram = TelegramNotifier()
                    telegram.send_message(
                        f"📬 Новое сообщение с контактов\n\n"
                        f"👤 Имя: {name}\n"
                        f"📧 Email: {email}\n"
                        f"💬 Сообщение:\n{message}"
                    )
                except Exception as e:
                    logger.error(f"Telegram notification error: {e}")
                
                messages.success(request, 'Спасибо! Ваше сообщение отправлено. Мы свяжемся с вами в ближайшее время.')
                return redirect('contact')
            else:
                # Если форма не валидна, показываем ошибки
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
        else:
            form = ContactForm()
        
        return render(request, "contact.html", {'form': form})
    except Exception as e:
        logger.error(f"Error in contact view: {e}")
        messages.error(request, 'Произошла ошибка при отправке сообщения')
        return render(request, "contact.html", {'form': ContactForm()})

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
                
        except Stone.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Камень не найден'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Метод не поддерживается'})

@login_required
def wishlist_view(request):
    """Страница избранного"""
    try:
        # Получаем все товары из избранного для текущего пользователя
        wishlist_items = Wishlist.objects.filter(
            user=request.user
        ).select_related('stone', 'stone__category')
        
        # Создаем безопасные slug для каждого камня
        for item in wishlist_items:
            item.stone.safe_slug = create_safe_slug(item.stone.name)
        
        context = {
            'wishlist_items': wishlist_items
        }
        return render(request, 'wishlist.html', context)
        
    except Exception as e:
        logger.error(f"Error in wishlist_view: {e}")
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
            
            session_key = request.session.session_key
            
            # Получаем или создаем сравнение
            comparison, created = Comparison.objects.get_or_create(
                session_key=session_key
            )
            
            # Проверяем есть ли уже
            if comparison.stones.filter(id=stone_id).exists():
                comparison.stones.remove(stone)
                return JsonResponse({
                    'success': True, 
                    'action': 'removed', 
                    'count': comparison.stones.count()
                })
            else:
                if comparison.stones.count() >= 4:
                    return JsonResponse({
                        'success': False, 
                        'error': 'Максимум 4 камня'
                    })
                
                comparison.stones.add(stone)
                return JsonResponse({
                    'success': True, 
                    'action': 'added', 
                    'count': comparison.stones.count()
                })
                
        except Stone.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Камень не найден'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Метод не поддерживается'})

def comparison_view(request):
    """Страница сравнения"""
    try:
        session_key = request.session.session_key
        stones = []
        
        if session_key:
            comparison = Comparison.objects.filter(session_key=session_key).first()
            if comparison:
                stones = comparison.stones.all().select_related('category')
        
        # Создаем безопасные slug для каждого камня
        for stone in stones:
            stone.safe_slug = create_safe_slug(stone.name)
        
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
        logger.error(f"Error in comparison_view: {e}")
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
        
        # Создаем безопасные slug для каждого камня в избранном
        for item in wishlist:
            item.stone.safe_slug = create_safe_slug(item.stone.name)
        
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
        
        # Создаем безопасные slug для каждого камня в заказах
        for order in orders:
            order.stone.safe_slug = create_safe_slug(order.stone.name)
        
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
        
        # Создаем безопасные slug для каждого камня в расчетах
        for calc in calculations:
            calc.stone.safe_slug = create_safe_slug(calc.stone.name)
        
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

@login_required
@require_POST
def delete_feedback(request, feedback_id):
    """Удаление отзыва/вопроса"""
    try:
        feedback = get_object_or_404(Feedback, id=feedback_id)
        
        # Проверяем права на удаление
        if not feedback.can_delete(request.user):
            return JsonResponse({
                'success': False, 
                'error': 'У вас нет прав на удаление этого отзыва'
            }, status=403)
        
        # Если это родительский отзыв, удаляем все ответы на него
        if feedback.replies.exists():
            feedback.replies.all().delete()
        
        feedback.delete()
        return JsonResponse({'success': True})
        
    except Feedback.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Отзыв не найден'}, status=404)
    except Exception as e:
        logger.error(f"Error deleting feedback: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
@require_POST
def reply_to_feedback(request, feedback_id):
    """Ответ на отзыв/вопрос"""
    try:
        parent = get_object_or_404(Feedback, id=feedback_id)
        
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        
        if not message:
            return JsonResponse({'success': False, 'error': 'Сообщение не может быть пустым'})
        
        # Создаем ответ
        reply = Feedback(
            request_type=parent.request_type,
            name=request.user.get_full_name() or request.user.username,
            numTel=request.user.phone or '',
            message=message,
            parent=parent,
            rating=None  # У ответов нет рейтинга
        )
        
        # Сохраняем с указанием пользователя для авто-модерации
        reply.save_with_user(request.user)
        
        # Отправляем уведомление автору оригинального отзыва (если есть email)
        if parent.user and parent.user.email:
            try:
                send_mail(
                    'Новый ответ на ваш отзыв',
                    f'Здравствуйте, {parent.name}!\n\nНа ваш отзыв ответил {reply.name}:\n\n{reply.message}',
                    settings.DEFAULT_FROM_EMAIL,
                    [parent.user.email],
                    fail_silently=True
                )
            except Exception as e:
                logger.error(f"Error sending email: {e}")
        
        return JsonResponse({
            'success': True,
            'reply': {
                'id': reply.id,
                'name': reply.name,
                'message': reply.message,
                'created_at': reply.created_at.strftime('%d.%m.%Y %H:%M'),
                'can_delete': reply.can_delete(request.user)
            }
        })
        
    except Feedback.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Отзыв не найден'}, status=404)
    except Exception as e:
        logger.error(f"Error in reply_to_feedback: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)