# Generated by Django 5.1.1 on 2024-09-25 15:31

import django.utils.timezone
from django.db import migrations, models

import sentry.db.models.fields.bounded
import sentry.db.models.fields.hybrid_cloud_foreign_key
from sentry.new_migrations.migrations import CheckedMigration


class Migration(CheckedMigration):
    # This flag is used to mark that a migration shouldn't be automatically run in production.
    # This should only be used for operations where it's safe to run the migration after your
    # code has deployed. So this should not be used for most operations that alter the schema
    # of a table.
    # Here are some things that make sense to mark as post deployment:
    # - Large data migrations. Typically we want these to be run manually so that they can be
    #   monitored and not block the deploy for a long period of time while they run.
    # - Adding indexes to large tables. Since this can take a long time, we'd generally prefer to
    #   run this outside deployments so that we don't block them. Note that while adding an index
    #   is a schema change, it's completely safe to run the operation after the code has deployed.
    # Once deployed, run these manually via: https://develop.sentry.dev/database-migrations/#migration-deployment

    is_post_deployment = False

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="FlagAuditLogModel",
            fields=[
                (
                    "id",
                    sentry.db.models.fields.bounded.BoundedBigAutoField(
                        primary_key=True, serialize=False
                    ),
                ),
                ("action", models.PositiveSmallIntegerField()),
                ("flag", models.CharField(max_length=100)),
                ("modified_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("modified_by", models.CharField(max_length=100)),
                ("modified_by_type", models.PositiveSmallIntegerField()),
                (
                    "organization_id",
                    sentry.db.models.fields.hybrid_cloud_foreign_key.HybridCloudForeignKey(
                        "sentry.Organization", db_index=True, on_delete="CASCADE"
                    ),
                ),
                ("tags", models.JSONField()),
            ],
            options={
                "db_table": "flags_audit_log",
                "indexes": [models.Index(fields=["flag"], name="flags_audit_flag_455822_idx")],
            },
        ),
    ]
