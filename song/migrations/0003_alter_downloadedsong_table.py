# Generated by Django 5.0.6 on 2024-06-07 10:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('song', '0002_alter_song_id'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='downloadedsong',
            table='downloaded_song',
        ),
    ]
