"""
URL configuration for StoneStore project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include
from Stone import views
from django.views.generic import TemplateView

said_bar = [
]

product_patterns = [
    path("", views.products, name="Вид изделий"),
    path("comments", views.comments, name="Комментарии"),
    # path("questions", views.questions, name="Вопросы о товаре"),
    path("new", views.new, name="Новые изделия"),
    path("top", views.top, name="Лучшее"),
]

urlpatterns = [
    path('index/', views.index, name="Домашняя страница"),
    path('admin/', admin.site.urls),
    path("user/", views.user, name="User"),
    path("user_response", views.user_response, name="Возращаем JSON"),
    path("products/<int:id>/", include(product_patterns)),
    path("by_product/", views.by_product, name='by_product'),
    path("questions/", views.questions, name="Вопросы/Отзывы"),
    re_path(r'^gallery|^galerey', views.galerey, name='gallery'),
    re_path(r'^about/contact', TemplateView.as_view(template_name = "contact.html")),
    re_path(r'^about', TemplateView.as_view(template_name = "about.html")),    
]


