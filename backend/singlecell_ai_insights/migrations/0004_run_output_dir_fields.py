from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("singlecell_ai_insights", "0003_run_started_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="run",
            name="output_dir_bucket",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="run",
            name="output_dir_key",
            field=models.CharField(blank=True, max_length=512),
        ),
        migrations.RemoveField(
            model_name="run",
            name="s3_report_key",
        ),
    ]
