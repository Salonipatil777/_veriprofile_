# Generated by Django 4.2.2 on 2023-10-12 13:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_ping'),
    ]

    operations = [
        migrations.AddField(
            model_name='ping',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='app.employee'),
        ),
    ]