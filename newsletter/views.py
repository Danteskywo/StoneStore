from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from .models import Subscriber, NewsletterCampaign, NewsletterTracking
import hashlib
import json

def subscribe(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        name = data.get('name', '')
        
        if not email:
            return JsonResponse({'success': False, 'error': 'Email обязателен'})
        
        subscriber, created = Subscriber.objects.get_or_create(
            email=email,
            defaults={'name': name}
        )
        
        if not created and not subscriber.is_active:
            subscriber.is_active = True
            subscriber.save()
        
        send_welcome_email(subscriber)
        
        return JsonResponse({
            'success': True,
            'message': 'Вы успешно подписались на рассылку!'
        })
    
    return JsonResponse({'success': False})

def unsubscribe(request):
    email = request.GET.get('email')
    token = request.GET.get('token')
    
    if not validate_unsubscribe_token(email, token):
        return render(request, 'newsletter/unsubscribe_error.html')
    
    try:
        subscriber = Subscriber.objects.get(email=email)
        subscriber.is_active = False
        subscriber.unsubscribed_at = timezone.now()
        subscriber.save()
        return render(request, 'newsletter/unsubscribe_success.html')
    except Subscriber.DoesNotExist:
        return render(request, 'newsletter/unsubscribe_error.html')

def track_open(request, tracking_id):
    try:
        tracking = NewsletterTracking.objects.get(id=tracking_id)
        tracking.opened_at = timezone.now()
        tracking.opened_count += 1
        tracking.save()
        response = HttpResponse(content_type='image/gif')
        response.write(b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b')
        return response
    except NewsletterTracking.DoesNotExist:
        return HttpResponse(status=404)

def track_click(request, tracking_id, link_id):
    try:
        tracking = NewsletterTracking.objects.get(id=tracking_id)
        tracking.clicked_at = timezone.now()
        tracking.clicked_count += 1
        if link_id not in tracking.clicked_links:
            tracking.clicked_links.append(link_id)
        tracking.save()
        return redirect('/')
    except NewsletterTracking.DoesNotExist:
        return HttpResponse(status=404)

def send_welcome_email(subscriber):
    subject = 'Добро пожаловать в StoneStore!'
    html_message = render_to_string('newsletter/welcome.html', {
        'subscriber': subscriber,
        'unsubscribe_url': generate_unsubscribe_url(subscriber.email)
    })
    plain_message = strip_tags(html_message)
    send_mail(
        subject,
        plain_message,
        'noreply@stonestore.ru',
        [subscriber.email],
        html_message=html_message,
        fail_silently=True
    )

def generate_unsubscribe_token(email):
    secret = 'your-secret-key'
    token = hashlib.md5(f"{email}{secret}".encode()).hexdigest()
    return token

def validate_unsubscribe_token(email, token):
    return token == generate_unsubscribe_token(email)

def generate_unsubscribe_url(email):
    token = generate_unsubscribe_token(email)
    return f"/newsletter/unsubscribe/?email={email}&token={token}"