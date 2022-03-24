# Generated by Django 3.2.10 on 2022-01-22 13:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('daiquiri_metadata', '0030_move_licenses_to_settings'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='column',
            options={'ordering': ('table__schema__order', 'table__order', 'order', 'name'), 'verbose_name': 'Column', 'verbose_name_plural': 'Columns'},
        ),
        migrations.AlterModelOptions(
            name='function',
            options={'ordering': ('order', 'name'), 'verbose_name': 'Function', 'verbose_name_plural': 'Functions'},
        ),
        migrations.AlterModelOptions(
            name='schema',
            options={'ordering': ('order', 'name'), 'verbose_name': 'Schema', 'verbose_name_plural': 'Schemas'},
        ),
        migrations.AlterModelOptions(
            name='table',
            options={'ordering': ('schema__order', 'order', 'name'), 'verbose_name': 'Table', 'verbose_name_plural': 'Tables'},
        ),
    ]