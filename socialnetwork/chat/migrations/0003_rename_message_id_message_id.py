# Generated by Django 5.0.2 on 2024-02-18 12:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_remove_message_id_message_message_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='message',
            old_name='message_id',
            new_name='id',
        ),
    ]