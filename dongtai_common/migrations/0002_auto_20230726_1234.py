# Generated by Django 3.2.20 on 2023-07-26 12:34

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import dongtai_common.utils.db


def add_admin_role(apps, schema_editor):
    from dongtai_common.models.role import IastRole, RoleStatus

    IastRole.objects.create(
        name="admin",
        is_admin=True,
        permission=[],
        status=RoleStatus.ENABLE,
    )


class Migration(migrations.Migration):
    dependencies = [
        ("dongtai_common", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="IastProjectGroup",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=255)),
                ("create_time", models.IntegerField(default=dongtai_common.utils.db.get_timestamp)),
            ],
            options={
                "db_table": "iast_project_group",
                "managed": True,
            },
        ),
        migrations.CreateModel(
            name="IastRole",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=255)),
                ("is_admin", models.BooleanField(default=False)),
                ("permission", models.JSONField()),
                ("status", models.IntegerField(choices=[(0, "禁用"), (1, "启用")])),
            ],
            options={
                "db_table": "iast_role",
                "managed": True,
            },
        ),
        migrations.AddField(
            model_name="user",
            name="is_global_permission",
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name="IastProjectUser",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                (
                    "project",
                    models.ForeignKey(
                        db_constraint=False,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="dongtai_common.iastproject",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        db_constraint=False, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
            options={
                "db_table": "iast_project_user",
                "managed": True,
            },
        ),
        migrations.CreateModel(
            name="IastProjectGroupUser",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                (
                    "project_group",
                    models.ForeignKey(
                        db_constraint=False,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="dongtai_common.iastprojectgroup",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        db_constraint=False, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
            options={
                "db_table": "iast_project_group_user",
                "managed": True,
            },
        ),
        migrations.CreateModel(
            name="IastProjectGroupProject",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                (
                    "project",
                    models.ForeignKey(
                        db_constraint=False,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="dongtai_common.iastproject",
                    ),
                ),
                (
                    "project_group",
                    models.ForeignKey(
                        db_constraint=False,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="dongtai_common.iastprojectgroup",
                    ),
                ),
            ],
            options={
                "db_table": "iast_project_group_project",
                "managed": True,
            },
        ),
        migrations.AddField(
            model_name="iastprojectgroup",
            name="create_user",
            field=models.ForeignKey(
                db_constraint=False, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="role",
            field=models.ForeignKey(
                db_constraint=False,
                default=1,
                on_delete=django.db.models.deletion.DO_NOTHING,
                to="dongtai_common.iastrole",
            ),
        ),
        migrations.RunPython(add_admin_role),
    ]
