# Generated by Django 4.2.2 on 2023-10-26 06:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0044_otheractivities'),
    ]

    operations = [
        migrations.AddField(
            model_name='experience',
            name='ex_job_industry',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
