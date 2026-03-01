from django.shortcuts import render, get_object_or_404
from Stone.models import Stone

def viewer_3d(request, stone_id=None):
    if stone_id:
        current_stone = get_object_or_404(Stone, id=stone_id)
    else:
        current_stone = Stone.objects.first()
    
    stones = Stone.objects.filter(in_stock=True)[:20]
    
    context = {
        'current_stone': current_stone,
        'stones': stones
    }
    return render(request, 'three_d_viewer/viewer.html', context)