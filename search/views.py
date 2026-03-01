from django.http import JsonResponse
from django.shortcuts import render
from Stone.models import Stone, StoneCategory
from .search_engine import SearchEngine

search_engine = SearchEngine()

def search_page(request):
    query = request.GET.get('q', '')
    
    filters = {}
    if request.GET.get('min_price'):
        filters['min_price'] = float(request.GET.get('min_price'))
    if request.GET.get('max_price'):
        filters['max_price'] = float(request.GET.get('max_price'))
    if request.GET.get('min_hardness'):
        filters['min_hardness'] = int(request.GET.get('min_hardness'))
    if request.GET.get('category'):
        filters['category'] = int(request.GET.get('category'))
    
    sort_by = request.GET.get('sort', 'relevance')
    page = int(request.GET.get('page', 1))
    
    results = search_engine.search(
        query=query,
        filters=filters,
        sort_by=sort_by,
        page=page
    )
    
    stone_ids = [r['id'] for r in results['results']]
    stones = Stone.objects.filter(id__in=stone_ids)
    stones_dict = {s.id: s for s in stones}
    ordered_stones = []
    for stone_id in stone_ids:
        if stone_id in stones_dict:
            ordered_stones.append(stones_dict[stone_id])
    
    categories = StoneCategory.objects.all()
    
    pages_range = range(1, results['pages'] + 1) if results['pages'] > 1 else []
    results['pages_range'] = pages_range
    
    context = {
        'query': query,
        'stones': ordered_stones,
        'results': results,
        'categories': categories,
        'filters': filters,
        'sort_by': sort_by
    }
    
    return render(request, 'search/search.html', context)

def api_search_suggest(request):
    query = request.GET.get('q', '')
    suggestions = search_engine.suggest(query)
    return JsonResponse({'suggestions': suggestions})

def api_search(request):
    query = request.GET.get('q', '')
    page = int(request.GET.get('page', 1))
    results = search_engine.search(query, page=page)
    return JsonResponse({
        'results': results['results'],
        'total': results['total'],
        'page': results['page'],
        'pages': results['pages']
    })