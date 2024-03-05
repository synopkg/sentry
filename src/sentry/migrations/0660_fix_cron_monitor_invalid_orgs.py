# Generated by Django 5.0.2 on 2024-03-01 23:48

from django.db import migrations

from sentry.new_migrations.migrations import CheckedMigration
from sentry.utils.query import RangeQuerySetWrapperWithProgressBarApprox


def fix_cron_monitor_invalid_orgs(apps, schema_editor) -> None:
    Monitor = apps.get_model("sentry", "Monitor")
    Project = apps.get_model("sentry", "Project")

    for monitor in RangeQuerySetWrapperWithProgressBarApprox(Monitor.objects.all()):
        try:
            project = Project.objects.get(id=monitor.project_id)
        except Project.DoesNotExist:
            continue

        if project.organization_id != monitor.organization_id:
            monitor.organization_id = project.organization_id
            monitor.save(update_fields=["organization_id"])


class Migration(CheckedMigration):
    # This flag is used to mark that a migration shouldn't be automatically run in production. For
    # the most part, this should only be used for operations where it's safe to run the migration
    # after your code has deployed. So this should not be used for most operations that alter the
    # schema of a table.
    # Here are some things that make sense to mark as dangerous:
    # - Large data migrations. Typically we want these to be run manually by ops so that they can
    #   be monitored and not block the deploy for a long period of time while they run.
    # - Adding indexes to large tables. Since this can take a long time, we'd generally prefer to
    #   have ops run this and not block the deploy. Note that while adding an index is a schema
    #   change, it's completely safe to run the operation after the code has deployed.
    is_dangerous = True

    dependencies = [
        ("sentry", "0659_artifactbundleindex_cleanup"),
    ]

    operations = [
        migrations.RunPython(
            fix_cron_monitor_invalid_orgs,
            migrations.RunPython.noop,
            hints={
                "tables": [
                    "sentry_monitor",
                ]
            },
        )
    ]
