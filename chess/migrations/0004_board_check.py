# Generated by Django 3.0.6 on 2021-02-18 03:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chess', '0003_board'),
    ]

    operations = [
        migrations.AddField(
            model_name='board',
            name='check',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]