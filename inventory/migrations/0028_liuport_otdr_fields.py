import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0027_userprofile_password_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='liuport',
            name='otdr_distance',
            field=models.CharField(blank=True, help_text='e.g. 2.5 km', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='liuport',
            name='otdr_image',
            field=models.FileField(blank=True, null=True, upload_to='liu_otdr_images/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'pdf'])]),
        ),
    ]
