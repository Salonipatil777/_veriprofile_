# Generated by Django 4.2.2 on 2023-10-27 09:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0045_experience_ex_job_industry'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='contact',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
