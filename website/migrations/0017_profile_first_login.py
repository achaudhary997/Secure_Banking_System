# Generated by Django 2.1 on 2018-11-01 00:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0016_auto_20181031_2351'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='first_login',
            field=models.BooleanField(default=True),
        ),
    ]
