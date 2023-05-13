# Generated by Django 4.2.1 on 2023-05-12 19:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0002_alter_reminder_datetime_alter_user_last_name_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="user",
            old_name="lang_code",
            new_name="language_code",
        ),
        migrations.AddField(
            model_name="user",
            name="is_bot",
            field=models.BooleanField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="user",
            name="city",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="users",
                to="api.city",
            ),
        ),
    ]
