from django.conf import settings

def languages(request):
    current_language = request.LANGUAGE_CODE
    
    languages = []
    for code, name in settings.LANGUAGES:
        languages.append({
            'code': code,
            'name': name,
            'active': code == current_language
        })
    
    return {
        'languages': languages,
        'current_language': current_language
    }