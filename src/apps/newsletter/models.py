import uuid

from django.db import models


class Newsletter(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    datetime_on = models.DateTimeField()
    text_newsletter = models.TextField()
    filter_clients = models.TextField()
    datetime_off = models.DateTimeField()

    class Meta:
        db_table = "newsletters"


class Client(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    number_phone = models.TextField(unique=True)
    code_operator = models.IntegerField()
    tag = models.TextField()
    time_zone = models.TextField()

    class Meta:
        db_table = "clients"


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    datetime_create = models.DateTimeField()
    status = models.TextField()
    id_newsletter = models.ForeignKey(Newsletter, on_delete=models.DO_NOTHING)
    id_client = models.ForeignKey(Client, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = "messages"
