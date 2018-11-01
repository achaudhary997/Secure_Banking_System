# Generated by Django 2.1 on 2018-10-31 23:51

from django.db import migrations, models
import website.models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0015_auto_20181031_2322'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='private_key',
            field=models.CharField(blank=True, default=website.models.generate_private_key, max_length=1000000),
        ),
    ]