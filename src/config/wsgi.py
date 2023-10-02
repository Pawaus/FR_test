"""
WSGI config for newsletter project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import threading
from .scheduled_tasks import start_checking_newsletters, start_checking_failed_messages
from utils.logger import logger_main
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

try:
    th1 = threading.Thread(target=start_checking_newsletters)
    th1.start()
except Exception as e:
    logger_main.error(
        'error_start_checking_newsletters: ' + str(e))
try:
    th2 = threading.Thread(target=start_checking_failed_messages)
    th2.start()
except Exception as e:
    logger_main.error(
        'error_start_schedule_94: ' + str(e))
application = get_wsgi_application()
