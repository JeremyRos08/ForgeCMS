from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('builder', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customcontenttype',
            name='config',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='customfield',
            name='config',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name='customfield',
            name='order',
            field=models.PositiveIntegerField(db_index=True, default=0),
        ),
    ]
