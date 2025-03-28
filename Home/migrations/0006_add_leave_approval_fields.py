from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('Home', '0005_sync_leave_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='leave',
            name='approved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_leaves', to='auth.user'),
        ),
        migrations.AddField(
            model_name='leave',
            name='approval_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='leave',
            name='comments',
            field=models.TextField(blank=True, null=True),
        ),
    ] 