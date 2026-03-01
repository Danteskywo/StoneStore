from django.shortcuts import render, redirect
from django.contrib import messages
from .models import MeasurementRequest
from Stone.models import Stone
from notifications.telegram_bot import TelegramNotifier

def measurement_request(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        address = request.POST.get('address')
        stone_id = request.POST.get('stone')
        product_type = request.POST.get('product_type')
        preferred_date = request.POST.get('preferred_date')
        preferred_time = request.POST.get('preferred_time')
        comment = request.POST.get('comment')
        
        measurement = MeasurementRequest.objects.create(
            name=name,
            phone=phone,
            email=email,
            address=address,
            stone_id=stone_id if stone_id else None,
            product_type=product_type,
            preferred_date=preferred_date if preferred_date else None,
            preferred_time=preferred_time,
            comment=comment
        )
        
        telegram = TelegramNotifier()
        text = f"""
<b>📏 НОВЫЙ ЗАПРОС НА ЗАМЕР #{measurement.id}</b>

👤 <b>Клиент:</b> {measurement.name}
📞 <b>Телефон:</b> {measurement.phone}
📧 <b>Email:</b> {measurement.email or 'не указан'}

📍 <b>Адрес:</b> {measurement.address}
🔨 <b>Тип:</b> {measurement.get_product_type_display()}
💎 <b>Камень:</b> {measurement.stone.name if measurement.stone else 'Не выбран'}

📅 <b>Предпочтительная дата:</b> {measurement.preferred_date or 'не указана'}
⏰ <b>Время:</b> {measurement.preferred_time or 'не указано'}

💬 <b>Комментарий:</b>
{measurement.comment or 'Нет'}
        """
        telegram.send_message(text)
        
        messages.success(request, 'Заявка на замер принята! Наш специалист свяжется с вами для подтверждения.')
        return redirect('measurement_success')
    
    stones = Stone.objects.filter(in_stock=True)
    context = {
        'stones': stones
    }
    return render(request, 'measurement/request.html', context)

def measurement_success(request):
    return render(request, 'measurement/success.html')

def measurement_guide(request):
    return render(request, 'measurement/guide.html')