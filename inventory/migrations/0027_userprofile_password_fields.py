from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0026_alter_junctionbox_jb_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='force_password_change',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='last_password_reset',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
