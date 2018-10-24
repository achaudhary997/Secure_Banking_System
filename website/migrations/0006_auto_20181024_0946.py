# Generated by Django 2.1 on 2018-10-24 09:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0005_auto_20181024_0843'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customerindividual',
            name='otp_secret',
        ),
        migrations.RemoveField(
            model_name='merchant',
            name='otp_secret',
        ),
        migrations.AddField(
            model_name='profile',
            name='otp_secret',
            field=models.CharField(default='NONE', max_length=16),
        ),
    ]