from django.core.management.base import BaseCommand
from Home.models import Leave
from django.db import connection

class Command(BaseCommand):
    help = 'Inspect the Leave model and database structure'

    def handle(self, *args, **options):
        # Check model fields
        self.stdout.write("Leave Model Fields:")
        for field in Leave._meta.get_fields():
            self.stdout.write(f"- {field.name}: {field.get_internal_type()}")

        # Check actual database columns
        self.stdout.write("\nDatabase Table Structure:")
        with connection.cursor() as cursor:
            cursor.execute("DESCRIBE Home_leave;")
            columns = cursor.fetchall()
            for column in columns:
                self.stdout.write(f"- {column[0]}: {column[1]}")

        # Check a sample of leave records
        self.stdout.write("\nSample Leave Records:")
        try:
            leaves = Leave.objects.all()[:5]
            for leave in leaves:
                self.stdout.write(f"ID: {leave.id}")
                self.stdout.write(f"Student: {leave.student}")
                self.stdout.write(f"Application Date: {leave.application_date}")
                self.stdout.write(f"From Date: {leave.from_date}")
                self.stdout.write(f"To Date: {leave.to_date}")
                self.stdout.write(f"Days: {leave.days}")
                self.stdout.write(f"Status: {leave.status}")
                self.stdout.write("-" * 30)

            self.stdout.write(f"Total number of leave records: {Leave.objects.count()}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error retrieving leave records: {e}")) 