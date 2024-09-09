# Generated by Django 4.2.8 on 2024-01-31 10:04

from django.db import migrations

from sentry.new_migrations.migrations import CheckedMigration


class Migration(CheckedMigration):
    # This flag is used to mark that a migration shouldn't be automatically run in production. For
    # the most part, this should only be used for operations where it's safe to run the migration
    # after your code has deployed. So this should not be used for most operations that alter the
    # schema of a table.
    # Here are some things that make sense to mark as post deployment:
    # - Large data migrations. Typically we want these to be run manually by ops so that they can
    #   be monitored and not block the deploy for a long period of time while they run.
    # - Adding indexes to large tables. Since this can take a long time, we'd generally prefer to
    #   have ops run this and not block the deploy. Note that while adding an index is a schema
    #   change, it's completely safe to run the operation after the code has deployed.
    is_post_deployment = False

    dependencies = [
        ("sentry", "0639_add_spec_version_to_dashboard_on_demand"),
    ]

    operations = [
        migrations.RenameIndex(
            model_name="controloutbox",
            new_name="sentry_cont_region__0c4512_idx",
            old_fields=("region_name", "shard_scope", "shard_identifier", "scheduled_for"),
        ),
        migrations.RenameIndex(
            model_name="controloutbox",
            new_name="sentry_cont_region__a95d82_idx",
            old_fields=("region_name", "shard_scope", "shard_identifier", "id"),
        ),
        migrations.RenameIndex(
            model_name="controloutbox",
            new_name="sentry_cont_region__1c1c72_idx",
            old_fields=(
                "region_name",
                "shard_scope",
                "shard_identifier",
                "category",
                "object_identifier",
            ),
        ),
        migrations.RenameIndex(
            model_name="group",
            new_name="sentry_grou_project_5eb75b_idx",
            old_fields=("project", "status", "substatus", "last_seen", "id"),
        ),
        migrations.RenameIndex(
            model_name="group",
            new_name="sentry_grou_project_5acaf7_idx",
            old_fields=("project", "status", "substatus", "id"),
        ),
        migrations.RenameIndex(
            model_name="group",
            new_name="sentry_grou_project_ff3fdf_idx",
            old_fields=("project", "status", "substatus", "type", "last_seen", "id"),
        ),
        migrations.RenameIndex(
            model_name="group",
            new_name="sentry_grou_status_48b516_idx",
            old_fields=("status", "substatus", "id"),
        ),
        migrations.RenameIndex(
            model_name="group",
            new_name="sentry_grou_status_e07f40_idx",
            old_fields=("status", "substatus", "first_seen"),
        ),
        migrations.RenameIndex(
            model_name="group",
            new_name="sentry_grou_project_4662d9_idx",
            old_fields=("project", "first_release"),
        ),
        migrations.RenameIndex(
            model_name="group",
            new_name="sentry_grou_project_81a5ed_idx",
            old_fields=("project", "status", "last_seen", "id"),
        ),
        migrations.RenameIndex(
            model_name="group",
            new_name="sentry_grou_project_41a5ce_idx",
            old_fields=("project", "id"),
        ),
        migrations.RenameIndex(
            model_name="group",
            new_name="sentry_grou_project_17d28d_idx",
            old_fields=("project", "status", "type", "last_seen", "id"),
        ),
        migrations.RenameIndex(
            model_name="grouphistory",
            new_name="sentry_grou_project_bbcf30_idx",
            old_fields=("project", "status", "release"),
        ),
        migrations.RenameIndex(
            model_name="grouphistory",
            new_name="sentry_grou_group_i_c61acb_idx",
            old_fields=("group", "status"),
        ),
        migrations.RenameIndex(
            model_name="grouphistory",
            new_name="sentry_grou_project_20b3f8_idx",
            old_fields=("project", "date_added"),
        ),
        migrations.RenameIndex(
            model_name="incidenttrigger",
            new_name="sentry_inci_alert_r_33da01_idx",
            old_fields=("alert_rule_trigger", "incident_id"),
        ),
        migrations.RenameIndex(
            model_name="organizationmembermapping",
            new_name="sentry_orga_organiz_ae9fe7_idx",
            old_fields=("organization_id", "user"),
        ),
        migrations.RenameIndex(
            model_name="organizationmembermapping",
            new_name="sentry_orga_organiz_7de26b_idx",
            old_fields=("organization_id", "email"),
        ),
        migrations.RenameIndex(
            model_name="projectartifactbundle",
            new_name="sentry_proj_project_f73d36_idx",
            old_fields=("project_id", "artifact_bundle"),
        ),
        migrations.RenameIndex(
            model_name="regionoutbox",
            new_name="sentry_regi_shard_s_e7412f_idx",
            old_fields=("shard_scope", "shard_identifier", "id"),
        ),
        migrations.RenameIndex(
            model_name="regionoutbox",
            new_name="sentry_regi_shard_s_bfff84_idx",
            old_fields=("shard_scope", "shard_identifier", "category", "object_identifier"),
        ),
        migrations.RenameIndex(
            model_name="regionoutbox",
            new_name="sentry_regi_shard_s_cd9995_idx",
            old_fields=("shard_scope", "shard_identifier", "scheduled_for"),
        ),
        migrations.RenameIndex(
            model_name="releaseartifactbundle",
            new_name="sentry_rele_organiz_291018_idx",
            old_fields=("organization_id", "release_name", "dist_name", "artifact_bundle"),
        ),
        migrations.RenameIndex(
            model_name="releaseprojectenvironment",
            new_name="sentry_rele_project_922a6a_idx",
            old_fields=("project", "unadopted", "environment"),
        ),
        migrations.RenameIndex(
            model_name="releaseprojectenvironment",
            new_name="sentry_rele_project_4bea8e_idx",
            old_fields=("project", "adopted", "environment"),
        ),
    ]
