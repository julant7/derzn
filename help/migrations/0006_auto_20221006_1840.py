# Generated by Django 3.2.4 on 2022-10-06 08:40

from django.db import migrations, models
import help.validators


class Migration(migrations.Migration):

    dependencies = [
        ('help', '0005_auto_20221006_1830'),
    ]

    operations = [
        migrations.AddField(
            model_name='helppage',
            name='id',
            field=models.BigAutoField(auto_created=True, default='0', primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='helppage',
            name='tag',
            field=models.CharField(max_length=20, unique=True, validators=[help.validators.validate_tag]),
        ),
        migrations.DeleteModel(
            name='TagsHelpPage',
        ),
    ]
