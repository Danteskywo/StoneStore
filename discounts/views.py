from django.http import JsonResponse
from .models import PromoCode
import json

# Промокоды отключены по требованию заказчика

def apply_promo(request):
    """Промокоды временно отключены"""
    return JsonResponse({
        'success': False,
        'error': 'Промокоды временно недоступны'
    })

def remove_promo(request):
    """Промокоды временно отключены"""
    return JsonResponse({
        'success': False,
        'error': 'Промокоды временно недоступны'
    })