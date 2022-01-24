# Generated by Django 3.2.10 on 2021-12-10 11:24

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Datalink',
            fields=[
                ('datalink_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('ID', models.CharField(db_index=True, max_length=256, verbose_name='Identifier')),
                ('access_url', models.CharField(max_length=256, verbose_name='Access URL')),
                ('service_def', models.CharField(blank=True, max_length=80, verbose_name='Service definition')),
                ('error_message', models.CharField(blank=True, max_length=256, verbose_name='Error message')),
                ('description', models.CharField(blank=True, max_length=256, verbose_name='Description')),
                ('semantics', models.CharField(blank=True, db_index=True, max_length=80, verbose_name='Semantics')),
                ('content_type', models.CharField(db_index=True, max_length=80, verbose_name='Content type')),
                ('content_length', models.IntegerField(verbose_name='Content length')),
            ],
            options={
                'db_table': 'datalink',
            },
        ),
    ]