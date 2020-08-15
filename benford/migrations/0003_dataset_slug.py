# Generated by Django 3.1 on 2020-08-14 18:54

import benford.utils
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benford', '0002_auto_20200814_1425'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='slug',
            field=models.CharField(default=benford.utils.generate_random_identifier, max_length=10, unique=True),
        ),
    ]