from django.db import migrations, models
import django.db.models.deletion
from django.utils import timezone

class Migration(migrations.Migration):
    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('Home', '0006_add_leave_approval_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='check_in',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='attendance',
            name='check_out',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='attendance',
            name='comment',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='attendance',
            name='created_at',
            field=models.DateTimeField(default=timezone.now),
        ),
        migrations.AddField(
            model_name='attendance',
            name='present',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='attendance',
            name='status',
            field=models.CharField(choices=[('present', 'Present'), ('absent', 'Absent'), ('leave', 'On Leave')], default='absent', max_length=10),
        ),
        migrations.AddField(
            model_name='attendance',
            name='updated_at',
            field=models.DateTimeField(default=timezone.now),
        ),
        migrations.AlterUniqueTogether(
            name='attendance',
            unique_together={('student', 'date')},
        ),
        migrations.AlterField(
            model_name='attendance',
            name='marked_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='marked_attendances', to='auth.user'),
        ),
    ] 