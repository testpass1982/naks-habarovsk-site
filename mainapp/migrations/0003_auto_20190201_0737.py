# Generated by Django 2.1.2 on 2019-02-01 07:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0002_post_secondery_main'),
    ]

    operations = [
        migrations.AddField(
            model_name='menu',
            name='menu_link',
            field=models.CharField(choices=[('ATTSP', 'Аттестация специалистов сварочного производства'), ('ATTSV', 'Аттестация сварщиков'), ('ATTSO', 'Аттестация сварочного оборудования'), ('ATTST', 'Аттестация технологий сварки'), ('ATTAP2', 'Аттестация в АП2'), ('OKSV', 'Оценка квалификаций')], default='NONE', max_length=100),
        ),
        migrations.AlterField(
            model_name='post',
            name='secondery_main',
            field=models.BooleanField(default=False, verbose_name='Опубликовать на главной как новость без картинки'),
        ),
    ]