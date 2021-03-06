# Generated by Django 2.1 on 2018-10-30 13:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0010_systemadmin'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employee',
            name='user',
        ),
        migrations.RemoveField(
            model_name='systemadmin',
            name='user',
        ),
        migrations.RemoveField(
            model_name='systemmanager',
            name='user',
        ),
        migrations.AlterField(
            model_name='customerindividual',
            name='relationship_manager',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='indi_customer_rel_man', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='merchant',
            name='relationship_manager',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='merchant_rel_man', to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='Employee',
        ),
        migrations.DeleteModel(
            name='SystemAdmin',
        ),
        migrations.DeleteModel(
            name='SystemManager',
        ),
    ]
