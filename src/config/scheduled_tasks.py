import datetime
import os
import time

import pycron
import uuid

from apps.newsletter.models import Newsletter, Message
from .celery_worker import send_messages_task
from celery import current_app
from utils.logger import logger_main
from django.utils import timezone

time_for_checking_newsletters_time = os.getenv("TIME_FOR_CHECKING_NEWSLETTERS")
time_for_checking_messages_failed_time = os.getenv("TIME_FOR_CHECKING_MESSAGES")


def start_checking_newsletters():
    logger_main.info("Start checking newsletters")
    while True:
        if pycron.is_now(time_for_checking_newsletters_time):
            newsletters = Newsletter.objects.all()
            for newsletter in newsletters:
                if newsletter.datetime_on < timezone.now() < newsletter.datetime_off:
                    messages = Message.objects.select_related("id_newsletter").filter(
                        id_newsletter__id=uuid.UUID(newsletter.id))
                    if len(messages) > 0:
                        continue
                    else:
                        send_messages_task(newsletter.id)
        time.sleep(60)


def start_checking_failed_messages():
    logger_main.info("Start checking failed messages")
    while True:
        if pycron.is_now(time_for_checking_messages_failed_time):
            messages_failed = Message.objects.select_related("id_newsletter").filter(status="FAILED")
            if len(messages_failed) > 0:
                logger_main.info(f"Found {len(messages_failed)} messages with failed status")
                for message in messages_failed:
                    if message.id_newsletter.datetime_on < timezone.now() < message.id_newsletter.datetime_off:
                        logger_main.info(f"Retrying message {str(message.id)}")
                        message.status = "RETRYING"
                        message.save()
                        current_app.send_task(
                            'send_messages_newsletter',
                            kwargs={"message_id": str(message.id)},
                            queue="celery")
        time.sleep(60)