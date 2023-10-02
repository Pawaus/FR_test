import datetime
import uuid

from ninja import Router
from domain.global_schemas import Error
from domain.newsletter import CreateNewsletter, DeleteNewsletter, UpdateNewsletter, NewsletterDefaultResponse, \
    ResultNewsletterStatistic, ResultNewslettersStatistic
from apps.newsletter.models import Newsletter, Client, Message
from utils.logger import logger_main
from django.http import HttpResponse
from django.db.models import Q
from utils.processing_newsletters import processing_newsletter_stats
from config.celery_worker import send_messages_task
from celery import current_app

api_newsletter = Router()


@api_newsletter.post("/create", response={200: NewsletterDefaultResponse, 422: Error}, summary="Create newsletter")
def create_newsletter(request, newsletter: CreateNewsletter):
    """
        To create newsletter, send in request:
         - id newsletter
         - datetime_on  - Дата и время начала рассылки
         - text_newsletter - текст рассылки
         - filter_clients - фильтр клиентов (тег или код оператора)
         - datetime_off - дата и время остановки рассылки
    """
    logger_main.info("POST request /api/newsletter/create")
    datetime_on = datetime.datetime.strptime(newsletter.datetime_on, "%H:%M:%S %d.%m.%Y")
    datetime_off = datetime.datetime.strptime(newsletter.datetime_off, "%H:%M:%S %d.%m.%Y")
    newsletter_db = Newsletter(datetime_on=datetime_on, text_newsletter=newsletter.text_newsletter,
                               filter_clients=newsletter.filter_clients, datetime_off=datetime_off)
    try:
        newsletter_db.save()
        logger_main.info(f"Newsletter id={str(newsletter_db.id)} saved in DB")
        if datetime_on < datetime.datetime.now() < datetime_off:
            send_messages_task(newsletter_db.id)
        return {"status": "ok"}
    except Exception as e:

        logger_main.error(f"Failed to save newsletter:{str(e)}")
        return 422, {"message": "Error on save newsletter"}


@api_newsletter.delete("/delete", response={204: None, 422: Error}, summary="Delete Newsletter from DB")
def delete_newsletter(request, newsletter: DeleteNewsletter):
    """Delete Newsletter from DB"""
    logger_main.info(f"DELETE request /api/newsletter/delete id={newsletter.id}")
    try:
        Newsletter.objects.filter(id=uuid.UUID(newsletter.id)).first().delete()
        logger_main.info(f"delete complete newsletter id={newsletter.id}")
        return HttpResponse(status=204)
    except Newsletter.DoesNotExist:
        logger_main.error(f"Failed to delete newsletter, id={newsletter.id}, not found in DB")
        return 422, {"message": "Newsletter not found"}
    except Exception as e:
        logger_main.error(f"Failed to delete newsletter:{str(e)}")
        return 422, {"message": "Newsletter not found"}


@api_newsletter.put("/update", response={200: NewsletterDefaultResponse, 422: Error}, summary="Update Newsletter info")
def update_client_info(request, newsletter: UpdateNewsletter):
    """
    To update newsletter info, send in request:
     - id newsletter
     - datetime_on (not required) - Дата и время начала рассылки
     - text_newsletter (not required) - текст рассылки
     - filter_clients (not required) - фильтр клиентов (тег или код оператора)
     - datetime_off (not required) - дата и время остановки рассылки
    """
    logger_main.info(f"PUT request /api/newsletter/update id={newsletter.id}")
    try:

        newsletter_db = Newsletter.objects.get(id=uuid.UUID(newsletter.id))
        datetime_on = datetime.datetime.strptime(newsletter.datetime_on,
                                                 "%H:%M:%S %d.%m.%Y") if newsletter.datetime_on and newsletter.datetime_on != "" else newsletter_db.datetime_on
        datetime_off = datetime.datetime.strptime(newsletter.datetime_off,
                                                  "%H:%M:%S %d.%m.%Y") if newsletter.datetime_off and newsletter.datetime_off != "" else newsletter_db.datetime_off
        newsletter_db.datetime_on = datetime_on
        newsletter_db.datetime_off = datetime_off
        newsletter_db.text_newsletter = newsletter.text_newsletter if newsletter.text_newsletter and newsletter.text_newsletter != "" else newsletter_db.text_newsletter
        newsletter_db.filter_clients = newsletter.text_newsletter if newsletter.filter_clients and newsletter.filter_clients != "" else newsletter_db.filter_clients
        newsletter_db.save()
        logger_main.info(f"Newsletter id={newsletter.id} updated")
        return {"status": "ok"}
    except Newsletter.DoesNotExist:
        logger_main.error(f"Failed update newsletter id={newsletter.id}, does not exist")
        return 422, {"message": "Newsletter not found"}
    except Exception as e:
        logger_main.error(f"Failed update newsletter id={newsletter.id}, exception: {str(e)}")
        return 422, {"message": "Newsletter not found"}


@api_newsletter.get("/statistic_all/", description="Get statistics by all newsletters",
                    response={200: ResultNewslettersStatistic, 422: Error})
def statistic_newsletters(request):
    """Get statistics for all newsletters"""
    logger_main.info("GET request /api/newsletter/statistic_all")
    try:
        newsletters = Newsletter.objects.all()

        result_processing_newsletters = []
        count_total_messages_done = 0
        count_total_messages_processing = 0
        count_total_unsend_messages = 0

        for newsletter in newsletters:
            result_processing = processing_newsletter_stats(str(newsletter.id))
            result_processing_newsletters.append({
                "id_newsletter": str(newsletter.id),
                "count_messages_done": result_processing.count_messages_done,
                "count_messages_processing": result_processing.count_messages_processing,
                "count_unsend_messages": result_processing.count_clients_total - result_processing.count_messages_done,
                "count_clients": result_processing.count_clients_total,
                "text_newsletter": newsletter.text_newsletter,
                "datetime_on": newsletter.datetime_on.strftime("%H:%M:%S %d.%m.%Y"),
                "datetime_off": newsletter.datetime_off.strftime("%H:%M:%S %d.%m.%Y"),
                "filter_clients": newsletter.filter_clients
            })
            count_total_messages_processing += result_processing.count_messages_processing
            count_total_messages_done += result_processing.count_messages_done
            count_total_unsend_messages += result_processing.count_clients_total - result_processing.count_messages_done
        logger_main.info("Success collect statistic for all newsletters")
        return {
            "count_total_messages_processing": count_total_messages_processing,
            "count_total_messages_done": count_total_messages_done,
            "count_total_unsend_messages": count_total_unsend_messages,
            "newsletters": result_processing_newsletters

        }
    except Exception as e:
        logger_main.error(f"Failed collect statistic newsletters, exception: {str(e)}")
        return 422, {"message": "Failed to collect statistics"}


@api_newsletter.get("/statistic_by_id/", description="Get statistic by id newsletter",
                    response={200: ResultNewsletterStatistic, 422: Error, 400: Error})
def statistic_newsletter(request, id: str = None):
    """Get statistics for newsletter by id"""
    logger_main.info(f"GET request /api/newsletter/statistic_by_id/ id={id}")
    if id:
        try:
            newsletter = Newsletter.objects.filter(id=id).first()
            if newsletter:
                result_processing = processing_newsletter_stats(str(id))
                logger_main.info(f"Success process statistic by id={id}")
                return {

                    "id_newsletter": id,
                    "count_messages_done": result_processing.count_messages_done,
                    "count_messages_processing": result_processing.count_messages_processing,
                    "count_unsend_messages": result_processing.count_clients_total - result_processing.count_messages_done,
                    "count_clients": result_processing.count_clients_total,
                    "text_newsletter": newsletter.text_newsletter,
                    "datetime_on": newsletter.datetime_on.strftime("%H:%M:%S %d.%m.%Y"),
                    "datetime_off": newsletter.datetime_off.strftime("%H:%M:%S %d.%m.%Y"),
                    "filter_clients": newsletter.filter_clients

                }
        except Newsletter.DoesNotExist:
            logger_main.error(f"Failed collect statistic by newsletter id={id}, does not exist")
            return 422, {"message": f"No newsletter with id={id}"}
        except Exception as e:
            logger_main.error(f"Failed collect statistic by newsletter id={id}, exception: {str(e)}")
            return 422, {"message": f"No newsletter with id={id}"}
    else:
        logger_main.error(f"Failed collect statistic by newsletter, value \"id\" not present")
        return 400, {"message": f"No id in request"}
