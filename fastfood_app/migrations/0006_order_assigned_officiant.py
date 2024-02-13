# Generated by Django 5.0.2 on 2024-02-13 04:08

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fastfood_app', '0005_remove_image_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='assigned_officiant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_orders', to=settings.AUTH_USER_MODEL),
        ),
    ]