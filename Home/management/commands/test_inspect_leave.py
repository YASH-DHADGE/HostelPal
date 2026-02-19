from django.test import TestCase
from django.core.management import call_command
from django.contrib.auth.models import User
from Home.models import Leave
from io import StringIO
import sys
from django.utils import timezone
from django.db import connection

class InspectLeaveCommandTest(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            username='teststudent',
            password='testpass123'
        )
        self.leave1 = Leave.objects.create(
            student=self.student,
            application_date=timezone.now().date(),
            from_date=timezone.now().date(),
            to_date=timezone.now().date() + timezone.timedelta(days=2),
            days=3,
            status='Pending'
        )
        self.leave2 = Leave.objects.create(
            student=self.student,
            application_date=timezone.now().date(),
            from_date=timezone.now().date() + timezone.timedelta(days=5),
            to_date=timezone.now().date() + timezone.timedelta(days=7),
            days=3,
            status='Approved'
        )

    def test_handle_happy_path(self):
        out = StringIO()
        sys.stdout = out
        call_command('inspect_leave')
        sys.stdout = sys.__stdout__

        output = out.getvalue()
        self.assertIn("Leave Model Fields:", output)
        self.assertIn("Database Table Structure:", output)
        self.assertIn("Sample Leave Records:", output)
        self.assertIn(f"ID: {self.leave1.id}", output)
        self.assertIn(f"Student: {self.leave1.student}", output)
        self.assertIn(f"Total number of leave records: 2", output)
        self.assertIn("student: ForeignKey", output)
        self.assertIn("application_date: DateField", output)

        # Verify database columns are shown
        with connection.cursor() as cursor:
            cursor.execute("DESCRIBE Home_leave;")
            columns = [col[0] for col in cursor.fetchall()]
            for column in columns:
                self.assertIn(column, output)

    def test_handle_empty_database(self):
        Leave.objects.all().delete()
        out = StringIO()
        sys.stdout = out
        call_command('inspect_leave')
        sys.stdout = sys.__stdout__

        output = out.getvalue()
        self.assertIn("Leave Model Fields:", output)
        self.assertIn("Database Table Structure:", output)
        self.assertIn("Sample Leave Records:", output)
        self.assertIn("Total number of leave records: 0", output)
        self.assertNotIn("ID:", output)  # No records should show IDs

    def test_handle_database_error(self):
        # Temporarily break the database connection
        original_cursor = connection.cursor
        def mock_cursor():
            raise Exception("Simulated database error")
        connection.cursor = mock_cursor

        out = StringIO()
        sys.stdout = out
        call_command('inspect_leave')
        sys.stdout = sys.__stdout__

        # Restore original cursor
        connection.cursor = original_cursor

        output = out.getvalue()
        self.assertIn("Leave Model Fields:", output)
        self.assertIn("Error retrieving leave records: Simulated database error", output)
        self.assertNotIn("Total number of leave records:", output)

    def test_handle_model_field_inspection(self):
        out = StringIO()
        sys.stdout = out
        call_command('inspect_leave')
        sys.stdout = sys.__stdout__

        output = out.getvalue()
        expected_fields = [
            'id', 'student', 'application_date', 'from_date',
            'to_date', 'days', 'status'
        ]
        for field in expected_fields:
            self.assertIn(f"- {field}:", output)

    def test_handle_database_structure_inspection(self):
        out = StringIO()
        sys.stdout = out
        call_command('inspect_leave')
        sys.stdout = sys.__stdout__

        output = out.getvalue()
        self.assertIn("Database Table Structure:", output)

        # Verify all actual database columns are shown
        with connection.cursor() as cursor:
            cursor.execute("DESCRIBE Home_leave;")
            columns = cursor.fetchall()
            for column in columns:
                self.assertIn(f"- {column[0]}: {column[1]}", output)