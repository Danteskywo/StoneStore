from django.shortcuts import render
from django.http import JsonResponse
from .models import ChatSession, ChatMessage
import json

def chat_widget(request):
    return render(request, 'chat/widget.html')

def get_or_create_chat(request):
    if request.user.is_authenticated:
        session, created = ChatSession.objects.get_or_create(
            user=request.user,
            status__in=['waiting', 'active']
        )
    else:
        if not request.session.session_key:
            request.session.create()
        session, created = ChatSession.objects.get_or_create(
            session_key=request.session.session_key,
            status__in=['waiting', 'active']
        )
    return session

def send_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        message_text = data.get('message')
        
        if not message_text:
            return JsonResponse({'success': False, 'error': 'Пустое сообщение'})
        
        session = get_or_create_chat(request)
        
        message = ChatMessage.objects.create(
            session=session,
            user=request.user if request.user.is_authenticated else None,
            message=message_text,
            is_operator=False
        )
        
        return JsonResponse({
            'success': True,
            'message': {
                'id': message.id,
                'text': message.message,
                'time': message.created_at.strftime('%H:%M'),
                'is_operator': False
            }
        })
    
    return JsonResponse({'success': False})

def get_messages(request):
    session = get_or_create_chat(request)
    last_id = int(request.GET.get('last_id', 0))
    messages = session.messages.filter(id__gt=last_id)
    
    return JsonResponse({
        'success': True,
        'messages': [{
            'id': m.id,
            'text': m.message,
            'time': m.created_at.strftime('%H:%M'),
            'is_operator': m.is_operator
        } for m in messages]
    })

def close_chat(request):
    if request.method == 'POST':
        session = get_or_create_chat(request)
        session.status = 'closed'
        session.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

def check_operator(request):
    session = get_or_create_chat(request)
    return JsonResponse({
        'success': True,
        'has_operator': session.status == 'active',
        'operator_name': session.operator.username if session.operator else None
    })