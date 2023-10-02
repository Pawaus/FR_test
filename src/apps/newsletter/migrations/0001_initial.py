# Generated by Django 4.2.4 on 2023-10-01 18:37

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('number_phone', models.TextField(unique=True)),
                ('code_operator', models.IntegerField()),
                ('tag', models.TextField()),
                ('time_zone', models.TextField()),
            ],
            options={
                'db_table': 'clients',
            },
        ),
        migrations.CreateModel(
            name='Newsletter',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('datetime_on', models.DateTimeField()),
                ('text_newsletter', models.TextField()),
                ('filter_clients', models.TextField()),
                ('datetime_off', models.DateTimeField()),
            ],
            options={
                'db_table': 'newsletters',
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('datetime_create', models.DateTimeField()),
                ('status', models.TextField()),
                ('id_client', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='newsletter.client')),
                ('id_newsletter', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='newsletter.newsletter')),
            ],
            options={
                'db_table': 'messages',
            },
        ),
    ]
