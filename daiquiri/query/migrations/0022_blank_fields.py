# Generated by Django 2.1.4 on 2019-05-28 09:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('daiquiri_query', '0021_django2'),
    ]

    operations = [
        migrations.AlterField(
            model_name='queryjob',
            name='actual_query',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='queryjob',
            name='native_query',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='queryjob',
            name='query',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='queryjob',
            name='query_language',
            field=models.CharField(blank=True, default='', max_length=16),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='queryjob',
            name='queue',
            field=models.CharField(blank=True, default='', max_length=16),
            preserve_default=False,
        ),
    ]
