# Generated by Django 3.2.4 on 2024-03-31 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drevo', '0129_templateobject_templates_that_use'),
    ]

    operations = [
        migrations.AlterField(
            model_name='templateobject',
            name='templates_that_use',
            field=models.ManyToManyField(blank=True, related_name='template_objects_set', to='drevo.Znanie', verbose_name='Включающие шаблоны'),
        ),
    ]
