from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('Home', '0003_alter_attendance_status'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            ALTER TABLE Home_leave 
            ADD COLUMN from_date DATE NULL,
            ADD COLUMN to_date DATE NULL,
            ADD COLUMN days INT NULL;
            """,
            reverse_sql="""
            ALTER TABLE Home_leave 
            DROP COLUMN from_date,
            DROP COLUMN to_date,
            DROP COLUMN days;
            """
        ),
    ] 