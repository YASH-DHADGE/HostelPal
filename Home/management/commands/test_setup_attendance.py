from django.test import TestCase
from django.core.management import call_command
from django.db import connection
from django.contrib.auth.models import User
import io
from contextlib import redirect_stdout

class SetupAttendanceCommandTest(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            username='student1',
            password='testpass123'
        )
        self.teacher = User.objects.create_user(
            username='teacher1',
            password='testpass456'
        )
        self.stdout = io.StringIO()

    def tearDown(self):
        with connection.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS Home_attendance")

    def test_handle_creates_new_table_when_not_exists(self):
        with redirect_stdout(self.stdout):
            call_command('setup_attendance')

        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES LIKE 'Home_attendance'")
            table_exists = cursor.fetchone()
            self.assertIsNotNone(table_exists)

            cursor.execute("SHOW COLUMNS FROM Home_attendance")
            columns = [column[0] for column in cursor.fetchall()]
            expected_columns = ['id', 'student_id', 'date', 'status', 'marked_by_id', 'created_at', 'updated_at']
            for column in expected_columns:
                self.assertIn(column, columns)

            cursor.execute("SELECT COLUMN_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Home_attendance' AND COLUMN_NAME = 'status'")
            status_type = cursor.fetchone()[0]
            self.assertEqual(status_type, "varchar(10)")

            cursor.execute("SELECT COLUMN_DEFAULT FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Home_attendance' AND COLUMN_NAME = 'status'")
            status_default = cursor.fetchone()[0]
            self.assertEqual(status_default, "'absent'")

            cursor.execute("SELECT CONSTRAINT_NAME FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS WHERE TABLE_NAME = 'Home_attendance' AND CONSTRAINT_TYPE = 'UNIQUE'")
            unique_constraint = cursor.fetchone()
            self.assertIsNotNone(unique_constraint)

        output = self.stdout.getvalue()
        self.assertIn('Creating new attendance table...', output)
        self.assertIn('Successfully created new attendance table', output)
        self.assertIn('Attendance table setup completed successfully', output)

    def test_handle_updates_existing_table_with_missing_columns(self):
        with connection.cursor() as cursor:
            cursor.execute("""
            CREATE TABLE Home_attendance (
                id integer AUTO_INCREMENT PRIMARY KEY,
                student_id integer NOT NULL REFERENCES auth_user(id)
            )
            """)

        with redirect_stdout(self.stdout):
            call_command('setup_attendance')

        with connection.cursor() as cursor:
            cursor.execute("SHOW COLUMNS FROM Home_attendance")
            columns = [column[0] for column in cursor.fetchall()]
            expected_columns = ['id', 'student_id', 'date', 'status', 'marked_by_id', 'created_at', 'updated_at']
            for column in expected_columns:
                self.assertIn(column, columns)

        output = self.stdout.getvalue()
        self.assertIn('Attendance table exists, checking columns...', output)
        self.assertIn('Adding required columns to the attendance table...', output)
        self.assertIn('Successfully added columns to attendance table', output)
        self.assertIn('Attendance table setup completed successfully', output)

    def test_handle_does_nothing_when_table_exists_with_all_columns(self):
        with connection.cursor() as cursor:
            cursor.execute("""
            CREATE TABLE Home_attendance (
                id integer AUTO_INCREMENT PRIMARY KEY,
                student_id integer NOT NULL REFERENCES auth_user(id),
                date date NOT NULL,
                status varchar(10) NOT NULL DEFAULT 'absent',
                marked_by_id integer NULL REFERENCES auth_user(id),
                created_at datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE(student_id, date)
            )
            """)

        with redirect_stdout(self.stdout):
            call_command('setup_attendance')

        output = self.stdout.getvalue()
        self.assertIn('Attendance table exists, checking columns...', output)
        self.assertIn('All necessary columns already exist in the attendance table', output)
        self.assertIn('Attendance table setup completed successfully', output)

    def test_handle_creates_table_with_correct_foreign_key_constraints(self):
        with redirect_stdout(self.stdout):
            call_command('setup_attendance')

        with connection.cursor() as cursor:
            cursor.execute("""
            SELECT TABLE_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE TABLE_NAME = 'Home_attendance' AND REFERENCED_TABLE_NAME IS NOT NULL
            """)
            fk_constraints = cursor.fetchall()

            self.assertEqual(len(fk_constraints), 2)
            self.assertIn(('Home_attendance', 'student_id', 'auth_user', 'id'), fk_constraints)
            self.assertIn(('Home_attendance', 'marked_by_id', 'auth_user', 'id'), fk_constraints)

    def test_handle_output_contains_success_messages(self):
        with redirect_stdout(self.stdout):
            call_command('setup_attendance')

        output = self.stdout.getvalue()
        self.assertIn('Setting up attendance table...', output)
        self.assertIn('Successfully created new attendance table', output)
        self.assertIn('Attendance table setup completed successfully', output)
        self.assertTrue(output.endswith('Attendance table setup completed successfully\n'))