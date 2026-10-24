from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('daiquiri_query', '0029_queryjob_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='downloadjob',
            name='processed_rows',
            field=models.PositiveBigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='queryarchivejob',
            name='processed_rows',
            field=models.PositiveBigIntegerField(default=0),
        ),
    ]
