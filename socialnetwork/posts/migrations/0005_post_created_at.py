# Generated by Django 5.0.2 on 2024-02-17 02:59

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_remove_post_likes_like'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2024, 2, 16, 12, 0)),
            preserve_default=False,
        ),
    ]
