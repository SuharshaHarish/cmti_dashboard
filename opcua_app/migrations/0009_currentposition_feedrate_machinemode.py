# Generated by Django 3.2.4 on 2021-09-19 23:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('opcua_app', '0008_auto_20210919_1611'),
    ]

    operations = [
        migrations.CreateModel(
            name='CurrentPosition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('x_axis', models.DecimalField(decimal_places=2, default=0, max_digits=6)),
                ('y_axis', models.DecimalField(decimal_places=2, default=0, max_digits=6)),
                ('z_axis', models.DecimalField(decimal_places=2, default=0, max_digits=6)),
                ('b_axis', models.DecimalField(decimal_places=2, default=0, max_digits=6)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='FeedRate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('x_axis', models.DecimalField(decimal_places=2, default=0, max_digits=6)),
                ('y_axis', models.DecimalField(decimal_places=2, default=0, max_digits=6)),
                ('z_axis', models.DecimalField(decimal_places=2, default=0, max_digits=6)),
                ('b_axis', models.DecimalField(decimal_places=2, default=0, max_digits=6)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='MachineMode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mode_value', models.IntegerField(choices=[(0, 'Jog'), (1, 'Mdi'), (2, 'Auto')])),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]