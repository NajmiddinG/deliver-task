# Generated by Django 5.0.2 on 2024-02-12 06:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fastfood_app', '0004_delivered'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='image',
            name='name',
        ),
    ]
