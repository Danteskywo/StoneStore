from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.core.cache import cache
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import CountertopOrder, Feedback, Stone
from notifications.telegram_bot import TelegramNotifier
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=CountertopOrder)
def handle_order_saved(sender, instance, created, **kwargs):
    """Обработка сохранения заказа"""
    try:
        # Отправка уведомления только для новых заказов
        if created:
            # Telegram
            telegram = TelegramNotifier()
            telegram.send_order_notification(instance)
            
            # Email (если указан)
            if instance.customer_email:
                subject = f'Заказ #{instance.id} принят - StoneStore'
                html_message = render_to_string('emails/order_confirmation.html', {
                    'order': instance
                })
                plain_message = strip_tags(html_message)
                
                send_mail(
                    subject,
                    plain_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [instance.customer_email],
                    html_message=html_message,
                    fail_silently=True
                )
        
        # Инвалидация кэша дашборда
        cache.delete('dashboard_stats')
        cache.delete('recent_orders')
        
        logger.info(f"Order {instance.id} processed successfully")
        
    except Exception as e:
        logger.error(f"Error in handle_order_saved: {e}")

@receiver(post_save, sender=Feedback)
def handle_feedback_saved(sender, instance, created, **kwargs):
    """Обработка сохранения отзыва"""
    try:
        if created:
            # Telegram уведомление
            telegram = TelegramNotifier()
            telegram.send_feedback_notification(instance)
        
        # Инвалидация кэша
        cache.delete('recent_reviews')
        cache.delete('feedback_stats')
        
        logger.info(f"Feedback {instance.id} processed successfully")
        
    except Exception as e:
        logger.error(f"Error in handle_feedback_saved: {e}")

@receiver(post_save, sender=Stone)
def handle_stone_saved(sender, instance, **kwargs):
    """Обработка сохранения камня"""
    try:
        # Инвалидация кэша поиска
        cache.delete('search_index')
        cache.delete('popular_stones')
        
        # Обновление поискового индекса
        from search.search_engine import SearchEngine
        search_engine = SearchEngine()
        search_engine.update_index()
        
    except Exception as e:
        logger.error(f"Error in handle_stone_saved: {e}")

@receiver(post_delete, sender=CountertopOrder)
@receiver(post_delete, sender=Feedback)
def handle_model_deleted(sender, instance, **kwargs):
    """Обработка удаления записей"""
    try:
        cache.delete('dashboard_stats')
        cache.delete('recent_orders')
        cache.delete('recent_reviews')
    except Exception as e:
        logger.error(f"Error in handle_model_deleted: {e}")

@receiver(pre_save, sender=CountertopOrder)
def handle_order_pre_save(sender, instance, **kwargs):
    """Предварительная обработка заказа"""
    try:
        # Автоматический расчет цены, если не указана
        if not instance.total_price:
            instance.total_price = instance.calculate_price()
            
    except Exception as e:
        logger.error(f"Error in handle_order_pre_save: {e}")