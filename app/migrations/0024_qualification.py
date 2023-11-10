# Generated by Django 4.2.2 on 2023-10-20 09:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0023_sociallinks'),
    ]

    operations = [
        migrations.CreateModel(
            name='Qualification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('degree', models.CharField(max_length=300, null=True)),
                ('specialization', models.CharField(max_length=500, null=True)),
                ('passing_year', models.CharField(max_length=500, null=True)),
                ('college', models.CharField(max_length=500, null=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.employee')),
            ],
        ),
    ]