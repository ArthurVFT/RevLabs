from django.db import migrations, models


def populate_source_lap_id(apps, schema_editor):
    """Give existing laps a stable source ID derived from legacy metadata."""
    TelemetryLap = apps.get_model('revlabs', 'TelemetryLap')
    for lap in TelemetryLap.objects.all().iterator():
        if lap.original_lap_id is None:
            continue
        if lap.original_session_id is not None:
            lap.source_lap_id = f"session-{lap.original_session_id}-lap-{lap.original_lap_id}"
        else:
            lap.source_lap_id = f"lap-{lap.original_lap_id}"
        lap.source = 'legacy'
        lap.save(update_fields=['source', 'source_lap_id'])


class Migration(migrations.Migration):

    dependencies = [
        ('revlabs', '0008_telemetrylap_sector_1_ms_telemetrylap_sector_2_ms_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='telemetrylap',
            name='source',
            field=models.CharField(
                blank=True,
                default='',
                help_text="Origin label from the import file (e.g. 'manual', 'bundle')",
                max_length=100,
            ),
        ),
        migrations.AddField(
            model_name='telemetrylap',
            name='source_lap_id',
            field=models.CharField(
                blank=True,
                help_text='Stable lap ID in the source file, used to avoid duplicate imports',
                max_length=200,
                null=True,
            ),
        ),
        migrations.AddIndex(
            model_name='telemetrylap',
            index=models.Index(
                fields=['car', 'track', 'source_lap_id'],
                name='revlabs_tl_car_track_srcid_idx',
            ),
        ),
        migrations.RunPython(populate_source_lap_id, migrations.RunPython.noop),
    ]
