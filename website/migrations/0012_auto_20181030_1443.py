# Generated by Django 2.1 on 2018-10-30 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0011_auto_20181030_1340'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profilemodificationreq',
            name='aadhar_number',
        ),
        migrations.AddField(
            model_name='profilemodificationreq',
            name='is_verified_admin',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='profilemodificationreq',
            name='is_verified_employee',
            field=models.IntegerField(default=0),
        ),
    ]