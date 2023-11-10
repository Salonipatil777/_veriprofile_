# Generated by Django 4.2.2 on 2023-11-07 07:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0048_employee_auth_token_employee_is_verified_email'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='notification',
            options={'ordering': ['-created_at']},
        ),
        migrations.RemoveField(
            model_name='notification',
            name='schedule_option',
        ),
        migrations.AlterField(
            model_name='notification',
            name='frequency_option',
            field=models.CharField(choices=[('week', 'A Week'), ('month', 'A Month'), ('year', 'A Year'), ('custom', 'Custom'), ('hourly', 'Hourly')], default='week', max_length=10),
        ),
    ]
