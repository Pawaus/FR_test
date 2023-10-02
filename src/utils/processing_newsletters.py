import uuid
from django.db.models import Q
from apps.newsletter.models import Newsletter, Client, Message


class ResultProcessingNewsletter:
    count_messages_processing: int
    count_messages_done: int
    count_clients_total: int


def processing_newsletter_stats(id_newsletter: str) -> ResultProcessingNewsletter:
    newsletter_db = Newsletter.objects.filter(id=uuid.UUID(id_newsletter)).first()
    clients = Client.objects.filter(
        Q(tag=newsletter_db.filter_clients) | Q(code_operator=newsletter_db.filter_clients)).all()
    messages_query = Message.objects.select_related('id_client', "id_newsletter").filter(
        Q(id_client__tag=newsletter_db.filter_clients) | Q(id_client__code_operator=newsletter_db.filter_clients)).filter(id_newsletter__id=uuid.UUID(id_newsletter))
    messages_processing = messages_query.filter(status="PROCESSING").all()
    messages_done = messages_query.filter(status="DONE").all()
    result = ResultProcessingNewsletter()
    result.count_messages_done = len(messages_done)
    result.count_clients_total = len(clients)
    result.count_messages_processing = len(messages_processing)
    return result
