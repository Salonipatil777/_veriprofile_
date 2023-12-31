# Generated by Django 4.2.2 on 2023-10-21 07:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0034_socialwork_remove_employee_social_work_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='honors',
            name='employee',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='app.employee'),
        ),
        migrations.AlterField(
            model_name='proofofwork',
            name='employee',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='app.employee'),
        ),
        migrations.AlterField(
            model_name='skills',
            name='employee',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='app.employee'),
        ),
        migrations.AlterField(
            model_name='socialwork',
            name='employee',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='app.employee'),
        ),
    ]
