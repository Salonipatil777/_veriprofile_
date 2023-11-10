# Generated by Django 4.2.2 on 2023-10-26 05:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0043_mediareferences_employee'),
    ]

    operations = [
        migrations.CreateModel(
            name='OtherActivities',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('act_type', models.CharField(max_length=200, null=True)),
                ('act_title', models.CharField(max_length=200, null=True)),
                ('act_link', models.URLField(null=True)),
                ('act_date', models.CharField(max_length=200, null=True)),
                ('employee', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='app.employee')),
            ],
        ),
    ]