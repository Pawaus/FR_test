from ninja import Schema
from typing import List


class CreateNewsletter(Schema):
    datetime_on: str = "15:00:00 10.09.2023"
    text_newsletter: str = "some text newsletter"
    filter_clients: str = "tag_user_ad"
    datetime_off: str = "15:00:00 10.09.2023"

class DeleteNewsletter(Schema):
    id: str


class UpdateNewsletter(Schema):
    id: str
    datetime_on: str = "15:00:00 10.09.2023"
    text_newsletter: str = "some text newsletter"
    filter_clients: str = "tag_user_ad"
    datetime_off: str = "15:00:00 10.09.2023"

class ResultNewsletterStatistic(Schema):
    id_newsletter: str
    count_messages_done: int
    count_messages_processing: int
    count_unsend_messages: int
    count_clients: int
    text_newsletter: str
    datetime_on: str
    datetime_off: str
    filter_clients: str

class ResultNewslettersStatistic(Schema):
    newsletters: List[ResultNewsletterStatistic]
    count_total_messages_processing: int
    count_total_messages_done: int
    count_total_unsend_messages: int


class NewsletterDefaultResponse(Schema):
    status: str = "ok"