from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from Stone import views as stone_views
from calculator import views as calc_views
from search import views as search_views
from chat import views as chat_views
from newsletter import views as newsletter_views
from discounts import views as discount_views
from stone_quiz import views as quiz_views
from three_d_viewer import views as three_d_views
from measurement import views as measurement_views
from admin_dashboard import views as dashboard_views
from core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin/dashboard/', dashboard_views.admin_dashboard, name='admin_dashboard'),
    path('i18n/', include('django.conf.urls.i18n')),
    path('set-language/', core_views.set_language, name='set_language'),
    path('accounts/', include('allauth.urls')),
    path('__debug__/', include('debug_toolbar.urls')),
]

urlpatterns += i18n_patterns(
    path('', stone_views.index, name='home'),
    path('index/', stone_views.index, name='index'),
    path('catalog/', stone_views.catalog, name='catalog'),
    path('catalog/<slug:slug>/', stone_views.stone_detail, name='stone_detail'),
    path('order/', stone_views.by_product, name='by_product'),
    path('order/success/<int:order_id>/', stone_views.order_success, name='order_success'),
    path('questions/', stone_views.questions, name='questions'),
    path('gallery/', stone_views.gallery, name='gallery'),
    path('about/', stone_views.about, name='about'),
    path('contact/', stone_views.contact, name='contact'),
    
    path('api/calculate-price/', calc_views.api_calculate_price, name='api_calculate'),
    path('api/save-calculation/', calc_views.api_save_calculation, name='api_save_calculation'),
    path('my-calculations/', calc_views.saved_calculations, name='saved_calculations'),
    
    path('search/', search_views.search_page, name='search'),
    path('api/search/suggest/', search_views.api_search_suggest, name='api_search_suggest'),
    path('api/search/', search_views.api_search, name='api_search'),
    
    path('wishlist/', stone_views.wishlist_view, name='wishlist'),
    path('wishlist/add/<int:stone_id>/', stone_views.add_to_wishlist, name='add_to_wishlist'),
    path('api/wishlist/check/<int:stone_id>/', stone_views.check_wishlist_status, name='check_wishlist'),
    
    path('compare/', stone_views.comparison_view, name='comparison'),
    path('compare/add/<int:stone_id>/', stone_views.add_to_comparison, name='add_to_comparison'),
    path('compare/remove/<int:stone_id>/', stone_views.remove_from_comparison, name='remove_from_comparison'),
    
    path('register/', stone_views.register, name='register'),
    path('login/', stone_views.login_view, name='login'),
    path('logout/', stone_views.logout_view, name='logout'),
    path('profile/', stone_views.profile, name='profile'),
    path('profile/edit/', stone_views.profile_edit, name='profile_edit'),
    path('profile/orders/', stone_views.profile_orders, name='profile_orders'),
    path('profile/calculations/', stone_views.profile_calculations, name='profile_calculations'),
    
    path('chat/send/', chat_views.send_message, name='chat_send'),
    path('chat/messages/', chat_views.get_messages, name='chat_messages'),
    path('chat/close/', chat_views.close_chat, name='chat_close'),
    path('chat/check-operator/', chat_views.check_operator, name='chat_check'),
    
    path('newsletter/subscribe/', newsletter_views.subscribe, name='subscribe'),
    path('newsletter/unsubscribe/', newsletter_views.unsubscribe, name='unsubscribe'),
    path('newsletter/track/open/<int:tracking_id>/', newsletter_views.track_open, name='track_open'),
    path('newsletter/track/click/<int:tracking_id>/<int:link_id>/', newsletter_views.track_click, name='track_click'),
    
    path('discounts/apply/', discount_views.apply_promo, name='apply_promo'),
    path('discounts/remove/', discount_views.remove_promo, name='remove_promo'),
    
    path('quiz/', quiz_views.quiz_start, name='quiz_start'),
    path('quiz/results/', quiz_views.quiz_results, name='quiz_results'),
    
    path('3d-viewer/', three_d_views.viewer_3d, name='3d_viewer'),
    path('3d-viewer/<int:stone_id>/', three_d_views.viewer_3d, name='3d_viewer_with_stone'),
    
    path('measurement/', measurement_views.measurement_request, name='measurement'),
    path('measurement/success/', measurement_views.measurement_success, name='measurement_success'),
    path('measurement/guide/', measurement_views.measurement_guide, name='measurement_guide'),
    
    prefix_default_language=True,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)