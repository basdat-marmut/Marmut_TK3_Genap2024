# Generated by Django 5.0.6 on 2024-06-07 09:38

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('playlist', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playlist',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]
