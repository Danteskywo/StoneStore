from django.shortcuts import redirect
from django.conf import settings
from django.utils.translation import activate

def set_language(request):
    """Смена языка сайта"""
    if request.method == 'POST':
        lang_code = request.POST.get('language')
        next_url = request.POST.get('next', '/')
        
        if lang_code and lang_code in dict(settings.LANGUAGES):
            # Устанавливаем язык в сессию и куки
            request.session['django_language'] = lang_code
            response = redirect(next_url)
            response.set_cookie('django_language', lang_code, max_age=365*24*60*60)
            return response
    
    return redirect('/')