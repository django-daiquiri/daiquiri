# Generated by Django 3.2.11 on 2022-01-17 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('daiquiri_datalink', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datalink',
            name='content_length',
            field=models.IntegerField(null=True, verbose_name='Content length'),
        ),
    ]