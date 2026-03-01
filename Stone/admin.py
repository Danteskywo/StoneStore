from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse
from .models import User, Stone, StoneCategory, StoneImage, CountertopOrder, Feedback, Wishlist, Comparison

class StoneImageInline(admin.TabularInline):
    model = StoneImage
    extra = 3
    fields = ['image', 'is_main', 'order']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px;">', obj.image.url)
        return "Нет изображения"
    image_preview.short_description = 'Превью'

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'phone', 'is_active', 'date_joined', 'order_count']
    list_filter = ['is_active', 'is_staff', 'email_notifications']
    search_fields = ['username', 'email', 'phone']
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('phone', 'avatar', 'birth_date', 'address', 
                      'email_notifications', 'sms_notifications')
        }),
    )
    
    def order_count(self, obj):
        from .models import CountertopOrder
        count = CountertopOrder.objects.filter(customer_phone=obj.phone).count()
        return count
    order_count.short_description = 'Заказов'

@admin.register(StoneCategory)
class StoneCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'slug', 'stones_count']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    list_editable = ['order']
    
    def stones_count(self, obj):
        return obj.stones.count()
    stones_count.short_description = 'Камней'

@admin.register(Stone)
class StoneAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price_per_sqm', 'in_stock', 'stock_quantity', 'is_popular', 'is_new', 'image_preview']
    list_filter = ['category', 'in_stock', 'is_popular', 'is_new', 'frost_resistance']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [StoneImageInline]
    list_editable = ['price_per_sqm', 'in_stock', 'is_popular', 'is_new']
    readonly_fields = ['created_at', 'updated_at', 'main_image_preview']
    
    fieldsets = (
        ('Основное', {
            'fields': ('category', 'name', 'slug', 'description', 'characteristics')
        }),
        ('Изображения', {
            'fields': ('main_image', 'main_image_preview')
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
        ('Калькулятор', {
            'fields': ('cutting_price_per_m', 'edge_processing_prices', 
                      'sink_cutout_price', 'hob_cutout_price', 'installation_price_per_m')
        }),
        ('Служебное', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def image_preview(self, obj):
        if obj.main_image:
            return format_html('<img src="{}" style="max-height: 50px;">', obj.main_image.url)
        return "Нет изображения"
    image_preview.short_description = 'Превью'
    
    def main_image_preview(self, obj):
        if obj.main_image:
            return format_html('<img src="{}" style="max-height: 200px;">', obj.main_image.url)
        return "Нет изображения"
    main_image_preview.short_description = 'Предпросмотр'
    
    actions = ['make_popular', 'make_new', 'update_prices']
    
    def make_popular(self, request, queryset):
        queryset.update(is_popular=True)
    make_popular.short_description = "Отметить как популярные"
    
    def make_new(self, request, queryset):
        queryset.update(is_new=True)
    make_new.short_description = "Отметить как новинки"
    
    def update_prices(self, request, queryset):
        for stone in queryset:
            stone.price_per_sqm *= 1.1  # Увеличить цену на 10%
            stone.save()
    update_prices.short_description = "Увеличить цены на 10%"

@admin.register(CountertopOrder)
class CountertopOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name', 'customer_phone', 'stone', 'total_price', 'status', 'created_at', 'action_buttons']
    list_filter = ['status', 'created_at', 'sink_type', 'edge_type']
    search_fields = ['customer_name', 'customer_phone', 'customer_email', 'id']
    readonly_fields = ['created_at', 'updated_at', 'calculated_price']
    list_editable = ['status']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Клиент', {
            'fields': ('customer_name', 'customer_phone', 'customer_email', 'customer_address')
        }),
        ('Заказ', {
            'fields': ('stone', 'length', 'width', 'thickness', 'edge_type', 'sink_type', 'cutouts')
        }),
        ('Финансы', {
            'fields': ('total_price', 'discount_amount', 'promo_code', 'calculated_price')
        }),
        ('Статус', {
            'fields': ('status', 'comment', 'created_at', 'updated_at')
        }),
    )
    
    def calculated_price(self, obj):
        return f"{obj.calculate_price():,.0f} ₽"
    calculated_price.short_description = 'Расчетная цена'
    
    def action_buttons(self, obj):
        return format_html(
            '<a class="button" href="{}" target="_blank">Просмотр</a>&nbsp;'
            '<a class="button" href="{}">Изменить статус</a>',
            reverse('admin:Stone_countertoporder_change', args=[obj.id]),
            reverse('admin:Stone_countertoporder_change', args=[obj.id])
        )
    action_buttons.short_description = 'Действия'
    
    actions = ['mark_as_processing', 'mark_as_completed', 'send_notification']
    
    def mark_as_processing(self, request, queryset):
        queryset.update(status='processing')
    mark_as_processing.short_description = "Отметить как 'В обработке'"
    
    def mark_as_completed(self, request, queryset):
        queryset.update(status='completed')
    mark_as_completed.short_description = "Отметить как 'Выполнен'"
    
    def send_notification(self, request, queryset):
        from notifications.telegram_bot import TelegramNotifier
        telegram = TelegramNotifier()
        for order in queryset:
            telegram.send_status_update(order)
    send_notification.short_description = "Отправить уведомление"

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['name', 'request_type', 'rating', 'moderation_status', 'is_published', 'created_at', 'image_preview']
    list_filter = ['request_type', 'rating', 'moderation_status', 'is_published', 'created_at']
    search_fields = ['name', 'message', 'numTel']
    readonly_fields = ['created_at', 'image_previews']
    list_editable = ['moderation_status', 'is_published']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Основное', {
            'fields': ('request_type', 'name', 'numTel', 'adress', 'message', 'rating')
        }),
        ('Модерация', {
            'fields': ('moderation_status', 'moderation_comment', 'is_published', 'is_verified', 'order')
        }),
        ('Изображения', {
            'fields': ('image1', 'image2', 'image3', 'image_previews')
        }),
        ('Служебное', {
            'fields': ('created_at',)
        }),
    )
    
    def image_preview(self, obj):
        if obj.image1:
            return format_html('<img src="{}" style="max-height: 30px;">', obj.image1.url)
        return "Нет"
    image_preview.short_description = 'Фото'
    
    def image_previews(self, obj):
        html = ''
        for i, img in enumerate([obj.image1, obj.image2, obj.image3]):
            if img:
                html += f'<img src="{img.url}" style="max-height: 100px; margin: 5px;">'
        return format_html(html)
    image_previews.short_description = 'Все фото'
    
    actions = ['approve_feedback', 'reject_feedback']
    
    def approve_feedback(self, request, queryset):
        queryset.update(moderation_status='approved', is_published=True)
    approve_feedback.short_description = "Одобрить выбранные отзывы"
    
    def reject_feedback(self, request, queryset):
        queryset.update(moderation_status='rejected', is_published=False)
    reject_feedback.short_description = "Отклонить выбранные отзывы"

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'stone', 'added_at']
    list_filter = ['added_at']
    search_fields = ['user__username', 'stone__name']
    raw_id_fields = ['user', 'stone']

@admin.register(Comparison)
class ComparisonAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_key', 'stones_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'session_key']
    filter_horizontal = ['stones']
    
    def stones_count(self, obj):
        return obj.stones.count()
    stones_count.short_description = 'Камней'