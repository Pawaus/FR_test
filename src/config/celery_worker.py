import datetime
import json
import os
import uuid

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django

django.setup()
from celery import Celery, shared_task, current_app
from apps.newsletter.models import Message, Newsletter, Client
from django.db.models import Q
from django.db import transaction
from utils.logger import logger_main
from django.utils import timezone
from config.config_env import URL_MESSAGE_SERVICE, TOKEN_MESSAGE_SERVICE
import requests
import pytz

# Set the default Django settings module for the 'celery' program.


app = Celery('config')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')
# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


@shared_task(name="send_messages_task")
def send_messages_task(newsletter_id: str):
    try:
        newsletter_db = Newsletter.objects.filter(id=uuid.UUID(newsletter_id)).first()
    except Newsletter.DoesNotExist:
        return False

    clients = Client.objects.filter(
        Q(tag=newsletter_db.filter_clients) | Q(code_operator=newsletter_db.filter_clients)).all()
    for client in clients:
        msg = Message()
        msg.status = "PROCESSING"
        msg.id_client = client
        msg.id_newsletter = newsletter_db
        msg.datetime_create = timezone.now()
        msg.save()
        transaction.on_commit(
            lambda: current_app.send_task(
                'send_messages_newsletter',
                kwargs={"message_id": str(msg.id)},
                queue="celery"))


@shared_task(name="send_messages_newsletter")
def send_messages(message_id):
    logger_main.info("start worker send ")
    try:
        msg = Message.objects.select_related("id_newsletter", "id_client").filter(id=uuid.UUID(message_id)).first()
    except Message.DoesNotExist:
        return False
    logger_main.info(f"sending message \"{msg.id_newsletter.text_newsletter} to {msg.id_client.number_phone}")
    try:
        body = {
            "id": 123333221,
            "phone": int(msg.id_client.number_phone),
            "text": msg.id_newsletter.text_newsletter
        }
        headers = {
            "Authorization": "Bearer " + TOKEN_MESSAGE_SERVICE,
            "Content-Type": "application/json"
        }
        request_url = URL_MESSAGE_SERVICE + str(123333221)
        response = requests.post(request_url, headers=headers, data=json.dumps(body))
        if response.status_code == 200:
            response = response.json()
            if response["code"] == 0 and response["message"] == "OK":

                msg.status = "DONE"
                msg.save()
            else:
                msg.status = "FAILED"
                msg.save()
                logger_main.error(f"Failed to send message: Response code != 0 or response message on OK")
        else:
            msg.status = "FAILED"
            msg.save()
            logger_main.error(f"Failed to send message: Status code of response {response.status_code}")
    except Exception as e:
        msg.status = "FAILED"
        msg.save()
        logger_main.error(f"Failed to send message: {str(e)}")
