# Generated by Django 2.0.1 on 2018-02-01 15:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_auto_20180201_2132'),
    ]

    operations = [
        migrations.RenameField(
            model_name='companylog',
            old_name='company_id',
            new_name='company',
        ),
    ]