# Generated by Django 3.1 on 2020-08-14 21:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benford', '0005_auto_20200814_2307'),
    ]

    operations = [
        migrations.AlterField(
            model_name='significantdigit',
            name='percentage',
            field=models.DecimalField(decimal_places=1, max_digits=4),
        ),
    ]
