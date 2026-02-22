from django.contrib import admin
from .models import Stone, StoneCategory, StoneImage, CountertopOrder, Feedback

class StoneImageInline(admin.TabularInline):
    model = StoneImage
    extra = 3

@admin.register(StoneCategory)
class StoneCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

@admin.register(Stone)
class StoneAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price_per_sqm', 'in_stock', 'is_popular', 'is_new']
    list_filter = ['category', 'in_stock', 'is_popular', 'is_new', 'frost_resistance']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [StoneImageInline]
    fieldsets = (
        ('Основное', {
            'fields': ('category', 'name', 'slug', 'description', 'characteristics')
        }),
        ('Изображения', {
            'fields': ('main_image',)
        }),
        ('Характеристики', {
            'fields': ('hardness', 'frost_resistance', 'water_absorption')
        }),
        ('Доступность', {
            'fields': ('available_finishes', 'available_thickness')
        }),
        ('Цена и наличие', {
            'fields': ('price_per_sqm', 'in_stock', 'stock_quantity')
        }),
        ('Маркировка', {
            'fields': ('is_popular', 'is_new')
        }),
    )

@admin.register(CountertopOrder)
class CountertopOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name', 'stone', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['customer_name', 'customer_phone']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Клиент', {
            'fields': ('customer_name', 'customer_phone', 'customer_email', 'customer_address')
        }),
        ('Заказ', {
            'fields': ('stone', 'length', 'width', 'thickness', 'edge_type', 'sink_type', 'cutouts')
        }),
        ('Статус', {
            'fields': ('status', 'comment', 'created_at', 'updated_at')
        }),
    )

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['name', 'request_type', 'rating', 'created_at', 'is_published']
    list_filter = ['request_type', 'rating', 'is_published', 'created_at']
    search_fields = ['name', 'message']
    actions = ['mark_published', 'mark_unpublished']
    
    def mark_published(self, request, queryset):
        queryset.update(is_published=True)
    mark_published.short_description = "Опубликовать выбранные отзывы"
    
    def mark_unpublished(self, request, queryset):
        queryset.update(is_published=False)
    mark_unpublished.short_description = "Скрыть выбранные отзывы"