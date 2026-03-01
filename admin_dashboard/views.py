from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
from Stone.models import CountertopOrder, Feedback, Stone
from calculator.models import SavedCalculation
from discounts.models import PromoCode

@staff_member_required
def admin_dashboard(request):
    total_orders = CountertopOrder.objects.count()
    total_revenue = CountertopOrder.objects.aggregate(Sum('total_price'))['total_price__sum'] or 0
    total_stones = Stone.objects.count()
    total_feedback = Feedback.objects.count()
    
    orders_by_status = list(CountertopOrder.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status'))
    
    thirty_days_ago = timezone.now() - timedelta(days=30)
    orders_by_day = list(CountertopOrder.objects.filter(
        created_at__gte=thirty_days_ago
    ).extra({'day': "date(created_at)"}).values('day').annotate(
        count=Count('id'),
        revenue=Sum('total_price')
    ).order_by('day'))
    
    for item in orders_by_day:
        item['day'] = item['day'].strftime('%Y-%m-%d')
    
    popular_stones = Stone.objects.annotate(
        order_count=Count('countertoporder'),
        order_revenue=Sum('countertoporder__total_price')
    ).order_by('-order_count')[:10]
    
    avg_rating = Feedback.objects.filter(rating__isnull=False).aggregate(Avg('rating'))['rating__avg'] or 0
    reviews_count = Feedback.objects.filter(request_type='review').count()
    questions_count = Feedback.objects.filter(request_type='question').count()
    
    total_promos = PromoCode.objects.count()
    active_promos = PromoCode.objects.filter(is_active=True).count()
    total_promo_uses = PromoCode.objects.aggregate(Sum('usage_count'))['usage_count__sum'] or 0
    
    total_calculations = SavedCalculation.objects.count()
    
    last_orders = CountertopOrder.objects.select_related('stone').order_by('-created_at')[:10]
    
    context = {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_stones': total_stones,
        'total_feedback': total_feedback,
        'orders_by_status': orders_by_status,
        'orders_by_day': orders_by_day,
        'popular_stones': popular_stones,
        'avg_rating': avg_rating,
        'reviews_count': reviews_count,
        'questions_count': questions_count,
        'total_promos': total_promos,
        'active_promos': active_promos,
        'total_promo_uses': total_promo_uses,
        'total_calculations': total_calculations,
        'last_orders': last_orders,
    }
    
    return render(request, 'admin/dashboard.html', context)