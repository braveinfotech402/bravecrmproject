from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('client_app', '0013_alter_lead_description'),  # update this to match the actual dependency
    ]

    operations = [
        migrations.AddField(
            model_name='lead',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
