import requests
from django.conf import settings

class TelegramNotifier:
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    def send_message(self, text, parse_mode='HTML'):
        url = f"{self.api_url}/sendMessage"
        data = {
            'chat_id': self.chat_id,
            'text': text,
            'parse_mode': parse_mode
        }
        
        try:
            response = requests.post(url, data=data)
            return response.json()
        except Exception as e:
            print(f"Telegram error: {e}")
            return None
    
    def send_order_notification(self, order):
        text = f"""
<b>🆕 НОВЫЙ ЗАКАЗ #{order.id}</b>

👤 <b>Клиент:</b> {order.customer_name}
📞 <b>Телефон:</b> {order.customer_phone}
📧 <b>Email:</b> {order.customer_email or 'не указан'}

💎 <b>Камень:</b> {order.stone.name}
📐 <b>Размеры:</b> {order.length} x {order.width} м
📏 <b>Толщина:</b> {order.thickness} мм
🔲 <b>Кромка:</b> {order.get_edge_type_display()}
🚰 <b>Мойка:</b> {order.get_sink_type_display()}

💰 <b>Примерная стоимость:</b> {order.calculate_price():,.0f} ₽

📅 <b>Дата:</b> {order.created_at.strftime('%d.%m.%Y %H:%M')}
        """
        return self.send_message(text)
    
    def send_feedback_notification(self, feedback):
        emoji = '📝' if feedback.request_type == 'review' else '❓'
        text = f"""
{emoji} <b>НОВЫЙ {'ОТЗЫВ' if feedback.request_type == 'review' else 'ВОПРОС'}</b>

👤 <b>Имя:</b> {feedback.name}
📞 <b>Телефон:</b> {feedback.numTel}

💬 <b>Сообщение:</b>
{feedback.message}

{'⭐ ' * feedback.rating if feedback.rating else ''}

📅 <b>Дата:</b> {feedback.created_at.strftime('%d.%m.%Y %H:%M')}
        """
        return self.send_message(text)
    
    def send_status_update(self, order):
        status_emojis = {
            'new': '🆕',
            'processing': '⚙️',
            'measurement': '📏',
            'production': '🔨',
            'delivery': '🚚',
            'completed': '✅',
            'cancelled': '❌'
        }
        
        emoji = status_emojis.get(order.status, '📦')
        
        text = f"""
{emoji} <b>СТАТУС ЗАКАЗА #{order.id} ИЗМЕНЕН</b>

👤 <b>Клиент:</b> {order.customer_name}
📞 <b>Телефон:</b> {order.customer_phone}

<b>Новый статус:</b> {order.get_status_display()}

<a href="https://stonestore.ru/admin/Stone/countertoporder/{order.id}/change/">Открыть в админке</a>
        """
        return self.send_message(text)