# Generated by Django 3.2.4 on 2023-10-25 18:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drevo', '0081_questiontoknowledge_need_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='questiontoknowledge',
            name='order',
            field=models.IntegerField(default=0, null=True, verbose_name='Порядок'),
        ),
    ]
