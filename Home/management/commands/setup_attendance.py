from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Creates or updates the attendance table in the database'

    def handle(self, *args, **options):
        self.stdout.write('Setting up attendance table...')
        
        with connection.cursor() as cursor:
            # Check if the table exists
            cursor.execute("SHOW TABLES LIKE 'Home_attendance'")
            table_exists = cursor.fetchone()
            
            if table_exists:
                self.stdout.write('Attendance table exists, checking columns...')
                
                # Check if columns exist
                cursor.execute("SHOW COLUMNS FROM Home_attendance LIKE 'student_id'")
                student_id_exists = cursor.fetchone()
                
                cursor.execute("SHOW COLUMNS FROM Home_attendance LIKE 'date'")
                date_exists = cursor.fetchone()
                
                if not student_id_exists or not date_exists:
                    self.stdout.write('Adding required columns to the attendance table...')
                    
                    if not student_id_exists:
                        cursor.execute("ALTER TABLE Home_attendance ADD COLUMN student_id integer NOT NULL REFERENCES auth_user(id)")
                    
                    if not date_exists:
                        cursor.execute("ALTER TABLE Home_attendance ADD COLUMN date date NOT NULL")
                    
                    cursor.execute("ALTER TABLE Home_attendance ADD COLUMN status varchar(10) NOT NULL DEFAULT 'absent'")
                    cursor.execute("ALTER TABLE Home_attendance ADD COLUMN marked_by_id integer NULL REFERENCES auth_user(id)")
                    cursor.execute("ALTER TABLE Home_attendance ADD COLUMN created_at datetime NOT NULL DEFAULT CURRENT_TIMESTAMP")
                    cursor.execute("ALTER TABLE Home_attendance ADD COLUMN updated_at datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
                    
                    # Add unique constraint
                    cursor.execute("ALTER TABLE Home_attendance ADD UNIQUE(student_id, date)")
                    
                    self.stdout.write(self.style.SUCCESS('Successfully added columns to attendance table'))
                else:
                    self.stdout.write('All necessary columns already exist in the attendance table')
            else:
                self.stdout.write('Creating new attendance table...')
                
                # Create table
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
                
                self.stdout.write(self.style.SUCCESS('Successfully created new attendance table'))
                
        self.stdout.write(self.style.SUCCESS('Attendance table setup completed successfully')) 