# Generated by Django 2.1 on 2018-10-30 10:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0008_transaction_transaction_mode'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='signator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='signator', to=settings.AUTH_USER_MODEL),
        ),
    ]
