# Generated by Django 3.2.4 on 2021-09-19 23:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('opcua_app', '0009_currentposition_feedrate_machinemode'),
    ]

    operations = [
        migrations.CreateModel(
            name='MachineDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('actPartProgram', models.CharField(default='', max_length=250)),
                ('workPName', models.CharField(default='', max_length=250)),
                ('progName', models.CharField(default='', max_length=250)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='MachineStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status_value', models.IntegerField(choices=[(0, 'Aborted'), (1, 'Halted'), (2, 'Running'), (3, 'Waiting'), (4, 'Interrupted')])),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
