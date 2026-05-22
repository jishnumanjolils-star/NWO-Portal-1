# Generated migration for manual cable entry support

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0028_liuport_otdr_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='liu',
            name='cable',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.cable'),
        ),
        migrations.AddField(
            model_name='liu',
            name='cable_manual_entry',
            field=models.CharField(blank=True, help_text='Manual cable reference when dropdown selection not used', max_length=255, null=True),
        ),
    ]
