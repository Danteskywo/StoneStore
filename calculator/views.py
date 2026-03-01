from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import json
from Stone.models import Stone
from .calculator_core import StoneCalculator
from .models import SavedCalculation

@csrf_exempt
def api_calculate_price(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            stone = Stone.objects.get(id=data['stone_id'])
            calculator = StoneCalculator(
                stone=stone,
                length=data['length'],
                width=data['width'],
                thickness=data['thickness'],
                edge_type=data.get('edge_type', 'straight')
            )
            result = calculator.calculate_total(
                has_sink=data.get('has_sink', False),
                has_hob=data.get('has_hob', False),
                need_install=data.get('need_install', False)
            )
            return JsonResponse({'success': True, 'data': result})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Метод не поддерживается'})

@login_required
@csrf_exempt
def api_save_calculation(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            stone = Stone.objects.get(id=data['stone_id'])
            calculator = StoneCalculator(
                stone=stone,
                length=data['length'],
                width=data['width'],
                thickness=data['thickness'],
                edge_type=data['edge_type']
            )
            result = calculator.calculate_total(
                has_sink=data.get('has_sink', False),
                has_hob=data.get('has_hob', False),
                need_install=data.get('need_install', False)
            )
            calculation = SavedCalculation.objects.create(
                user=request.user,
                stone=stone,
                name=data.get('name', f'Расчет от {data["length"]}x{data["width"]}'),
                length=data['length'],
                width=data['width'],
                thickness=data['thickness'],
                edge_type=data['edge_type'],
                has_sink_cutout=data.get('has_sink', False),
                has_hob_cutout=data.get('has_hob', False),
                need_installation=data.get('need_install', False),
                total_price=result['total']
            )
            return JsonResponse({'success': True, 'id': calculation.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Метод не поддерживается'})

@login_required
def saved_calculations(request):
    calculations = SavedCalculation.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'calculator/saved_calculations.html', {'calculations': calculations})