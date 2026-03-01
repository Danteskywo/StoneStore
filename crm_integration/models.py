from django.db import models
from Stone.models import CountertopOrder, Feedback
import requests
from django.conf import settings

class CRMLog(models.Model):
    order = models.ForeignKey(CountertopOrder, on_delete=models.SET_NULL, null=True, blank=True)
    feedback = models.ForeignKey(Feedback, on_delete=models.SET_NULL, null=True, blank=True)
    
    crm_type = models.CharField(max_length=50, choices=[
        ('amo', 'AmoCRM'),
        ('bitrix', 'Bitrix24'),
        ('telegram', 'Telegram')
    ])
    
    request_data = models.JSONField()
    response_data = models.JSONField(null=True, blank=True)
    status_code = models.IntegerField(null=True, blank=True)
    success = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Лог CRM'
        verbose_name_plural = 'Логи CRM'
    
    def __str__(self):
        return f"Лог #{self.id} - {self.crm_type} - {'✅' if self.success else '❌'}"

class AmoCRMIntegration:
    def __init__(self):
        self.subdomain = settings.AMOCRM_SUBDOMAIN
        self.client_id = settings.AMOCRM_CLIENT_ID
        self.client_secret = settings.AMOCRM_CLIENT_SECRET
        self.redirect_uri = settings.AMOCRM_REDIRECT_URI
        self.access_token = self.get_access_token()
    
    def get_access_token(self):
        return None
    
    def create_lead(self, order):
        url = f"https://{self.subdomain}.amocrm.ru/api/v4/leads"
        data = {
            "name": f"Заказ #{order.id} - {order.customer_name}",
            "price": order.calculate_price(),
            "custom_fields_values": [
                {
                    "field_id": "телефон",
                    "values": [{"value": order.customer_phone}]
                },
                {
                    "field_id": "камень",
                    "values": [{"value": order.stone.name}]
                },
                {
                    "field_id": "размеры",
                    "values": [{"value": f"{order.length} x {order.width} м"}]
                }
            ]
        }
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            CRMLog.objects.create(
                order=order,
                crm_type='amo',
                request_data=data,
                response_data=response.json() if response.text else None,
                status_code=response.status_code,
                success=response.status_code == 200
            )
            return response.json()
        except Exception as e:
            CRMLog.objects.create(
                order=order,
                crm_type='amo',
                request_data=data,
                error_message=str(e),
                success=False
            )
            return None

class Bitrix24Integration:
    def __init__(self):
        self.webhook_url = settings.BITRIX24_WEBHOOK_URL
    
    def create_lead(self, order):
        url = f"{self.webhook_url}/crm.lead.add.json"
        data = {
            "fields": {
                "TITLE": f"Заказ #{order.id} - {order.customer_name}",
                "NAME": order.customer_name,
                "PHONE": [{"VALUE": order.customer_phone, "VALUE_TYPE": "WORK"}],
                "EMAIL": [{"VALUE": order.customer_email, "VALUE_TYPE": "WORK"}] if order.customer_email else [],
                "COMMENTS": f"Камень: {order.stone.name}\nРазмеры: {order.length}x{order.width}м\nТолщина: {order.thickness}мм",
                "SOURCE_ID": "WEB",
                "ASSIGNED_BY_ID": 1
            }
        }
        
        try:
            response = requests.post(url, json=data)
            CRMLog.objects.create(
                order=order,
                crm_type='bitrix',
                request_data=data,
                response_data=response.json(),
                status_code=response.status_code,
                success=response.status_code == 200
            )
            return response.json()
        except Exception as e:
            CRMLog.objects.create(
                order=order,
                crm_type='bitrix',
                request_data=data,
                error_message=str(e),
                success=False
            )
            return None