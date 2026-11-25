from django.db import migrations, models


def populate_usernames(apps, schema_editor):
    """Assign unique email addresses to existing users' internal usernames."""
    User = apps.get_model("accounts", "User")
    users = User.objects.using(schema_editor.connection.alias)
    for user in users.all().iterator():
        users.filter(pk=user.pk).update(username=user.email)


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0002_alter_user_managers_remove_user_username_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="username",
            field=models.CharField(max_length=254, unique=True, null=True),
        ),
        migrations.RunPython(populate_usernames, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="user",
            name="username",
            field=models.CharField(max_length=254, unique=True),
        ),
    ]
