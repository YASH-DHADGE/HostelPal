from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('Home', '0004_add_missing_leave_fields'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            UPDATE Home_leave 
            SET from_date = start_date 
            WHERE from_date IS NULL AND start_date IS NOT NULL;
            
            UPDATE Home_leave 
            SET to_date = end_date 
            WHERE to_date IS NULL AND end_date IS NOT NULL;
            
            UPDATE Home_leave 
            SET days = DATEDIFF(to_date, from_date) + 1 
            WHERE days IS NULL AND to_date IS NOT NULL AND from_date IS NOT NULL;
            """,
            reverse_sql=""
        ),
    ] 