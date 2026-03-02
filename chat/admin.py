from django.contrib import admin
from .models import ChatSession, ChatMessage

class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ['user', 'message', 'is_operator', 'created_at']
    fields = ['user', 'message', 'is_operator', 'created_at']
    can_delete = True
    
    def has_add_permission(self, request, obj=None):
        return True

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_key', 'operator', 'status', 'message_count', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'session_key']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ChatMessageInline]
    list_editable = ['status']
    
    fieldsets = (
        ('Информация о сессии', {
            'fields': ('user', 'session_key', 'operator', 'status')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Сообщений'
    
    actions = ['assign_to_me', 'close_chats', 'mark_as_active']
    
    def assign_to_me(self, request, queryset):
        queryset.update(operator=request.user, status='active')
        self.message_user(request, f"Вы назначены оператором для {queryset.count()} чатов")
    assign_to_me.short_description = "Назначить меня оператором"
    
    def close_chats(self, request, queryset):
        queryset.update(status='closed')
        self.message_user(request, f"{queryset.count()} чатов закрыто")
    close_chats.short_description = "Закрыть выбранные чаты"
    
    def mark_as_active(self, request, queryset):
        queryset.update(status='active')
    mark_as_active.short_description = "Отметить как активные"

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'user', 'short_message', 'is_operator', 'created_at']
    list_filter = ['is_operator', 'created_at']
    search_fields = ['message', 'user__username']
    readonly_fields = ['created_at']
    raw_id_fields = ['session', 'user']
    
    fieldsets = (
        ('Информация о сообщении', {
            'fields': ('session', 'user', 'is_operator')
        }),
        ('Сообщение', {
            'fields': ('message',)
        }),
        ('Время', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def short_message(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    short_message.short_description = 'Сообщение'
    
    actions = ['mark_as_operator', 'mark_as_user']
    
    def mark_as_operator(self, request, queryset):
        queryset.update(is_operator=True)
    mark_as_operator.short_description = "Отметить как сообщения оператора"
    
    def mark_as_user(self, request, queryset):
        queryset.update(is_operator=False)
    mark_as_user.short_description = "Отметить как сообщения пользователя"