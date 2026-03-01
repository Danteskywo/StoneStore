from django.http import JsonResponse
from .models import PromoCode
import json

def apply_promo(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        code = data.get('code')
        order_amount = float(data.get('amount', 0))
        
        try:
            promo = PromoCode.objects.get(code=code.upper())
        except PromoCode.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Промокод не найден'
            })
        
        is_valid, message = promo.is_valid(request.user if request.user.is_authenticated else None, order_amount)
        
        if not is_valid:
            return JsonResponse({
                'success': False,
                'error': message
            })
        
        discount = promo.calculate_discount(order_amount)
        request.session['applied_promo'] = {
            'code': promo.code,
            'discount': float(discount)
        }
        
        return JsonResponse({
            'success': True,
            'discount': discount,
            'final_price': order_amount - discount,
            'message': f'Промокод применен! Скидка: {discount} ₽'
        })
    
    return JsonResponse({'success': False})

def remove_promo(request):
    if 'applied_promo' in request.session:
        del request.session['applied_promo']
    return JsonResponse({'success': True})