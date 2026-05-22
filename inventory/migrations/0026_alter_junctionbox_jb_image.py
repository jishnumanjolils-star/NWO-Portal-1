import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0025_ebcircuit_is_ring_ebcircuit_ring_image_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='junctionbox',
            name='jb_image',
            field=models.FileField(blank=True, null=True, upload_to='jb_uploads/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'pdf'])]),
        ),
    ]
