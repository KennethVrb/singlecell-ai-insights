import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('singlecell_ai_insights', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Run',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('run_id', models.CharField(max_length=128, unique=True)),
                ('name', models.CharField(blank=True, max_length=255)),
                ('status', models.CharField(blank=True, max_length=64)),
                ('pipeline', models.CharField(blank=True, max_length=255)),
                (
                    'created_at',
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('s3_report_key', models.CharField(blank=True, max_length=512)),
                (
                    'metadata',
                    models.JSONField(blank=True, default=dict),
                ),
                (
                    'normalized_context',
                    models.JSONField(blank=True, null=True),
                ),
                ('indexed_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
