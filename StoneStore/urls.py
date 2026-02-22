from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from Stone import views

urlpatterns = [
    path('', views.index, name='home'),
    path('index/', views.index, name='index'),
    path('admin/', admin.site.urls),
    
    # Каталог
    path('catalog/', views.catalog, name='catalog'),
    path('catalog/<slug:slug>/', views.stone_detail, name='stone_detail'),
    
    # Заказы
    path('order/', views.by_product, name='by_product'),
    path('order/success/<int:order_id>/', views.order_success, name='order_success'),
    
    # Отзывы
    path('questions/', views.questions, name='questions'),
    
    # Галерея
    path('gallery/', views.gallery, name='gallery'),
    
    # Инфо
    path('about/', views.about, name='about'),
    path('about/contact/', views.contact, name='contact'),
    
    # API
    path('api/calculate-price/', views.calculate_price, name='calculate_price'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)