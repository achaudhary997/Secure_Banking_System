# Generated by Django 2.1 on 2018-10-24 08:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0004_auto_20181024_0834'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customerindividual',
            name='otp_secret',
            field=models.CharField(default='NONE', max_length=16),
        ),
        migrations.AlterField(
            model_name='merchant',
            name='otp_secret',
            field=models.CharField(default='NONE', max_length=16),
        ),
    ]
