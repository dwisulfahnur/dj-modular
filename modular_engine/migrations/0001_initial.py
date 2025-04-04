# Generated by Django 5.1.7 on 2025-03-13 07:19

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Module',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('module_id', models.CharField(max_length=100, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('version', models.CharField(max_length=50)),
                ('status', models.CharField(choices=[('installed', 'Installed'), ('not_installed', 'Not Installed'), ('upgrade_available', 'Upgrade Available')], default='not_installed', max_length=20)),
                ('install_date', models.DateTimeField(blank=True, null=True)),
                ('update_date', models.DateTimeField(blank=True, null=True)),
            ],
        ),
    ]
