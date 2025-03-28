from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Complaint(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE, null=True)
    complaint_type = models.CharField(max_length=100)
    description = models.TextField()
    resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    reply = models.TextField(null=True, blank=True)
    replied_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.complaint_type

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    room_number = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=15)
    address = models.TextField(null=True, blank=True)
    parent_name = models.CharField(max_length=100, null=True, blank=True)
    parent_phone_number = models.CharField(max_length=15, null=True, blank=True)
    emergency_contact_name = models.CharField(max_length=100, null=True, blank=True)
    emergency_contact_number = models.CharField(max_length=15, null=True, blank=True)
    registration_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.user.username
    
class Leave(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='leave_applications')
    application_date = models.DateTimeField(default=timezone.now)
    from_date = models.DateField(null=True, blank=True)
    to_date = models.DateField(null=True, blank=True)
    days = models.IntegerField(null=True, blank=True)
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='approved_leaves')
    approval_date = models.DateTimeField(null=True, blank=True)
    comments = models.TextField(blank=True, null=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if self.start_date and not self.from_date:
            self.from_date = self.start_date
        elif self.from_date:
            self.start_date = self.from_date
            
        if self.end_date and not self.to_date:
            self.to_date = self.end_date
        elif self.to_date:
            self.end_date = self.to_date
            
        if not self.days and self.from_date and self.to_date:
            delta = (self.to_date - self.from_date).days + 1
            self.days = delta
            
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.student.username} - {self.from_date or 'Unknown'} to {self.to_date or 'Unknown'}"

class Attendance(models.Model):
    ATTENDANCE_STATUS = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('leave', 'On Leave'),
    )
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=ATTENDANCE_STATUS, default='absent')
    marked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='marked_attendances')
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    present = models.BooleanField(default=False)  # Legacy field for backward compatibility
    
    class Meta:
        unique_together = ['student', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.student.username} - {self.date} - {self.status}"
    
    def save(self, *args, **kwargs):
        # Ensure the present field stays in sync with status
        self.present = (self.status == 'present')
        if not self.pk:  # Only for new records
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

class Message(models.Model):
    sender = models.ForeignKey(Student, on_delete=models.CASCADE)  # Or User, if you prefer
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    # You might also want to add a field for the group or room the message belongs to

class Chat(models.Model):
    message = models.TextField()
    student = models.ForeignKey('Student', on_delete=models.CASCADE, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    student_name = models.CharField(max_length=100, null=True, blank=True)
    sender_type = models.CharField(max_length=10, choices=[
        ('STUDENT', 'Student'), 
        ('WARDEN', 'Warden')
    ], default='STUDENT')

class Payment(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()

class Notice(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)
    important = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title

class Feedback(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    category = models.CharField(max_length=100, choices=[
        ('MESS', 'Mess/Food'),
        ('FACILITIES', 'Facilities'),
        ('CLEANLINESS', 'Cleanliness'),
        ('SECURITY', 'Security'),
        ('STAFF', 'Staff Behavior')
    ])
    rating = models.IntegerField(choices=[
        (1, '1 Star'), 
        (2, '2 Stars'), 
        (3, '3 Stars'), 
        (4, '4 Stars'), 
        (5, '5 Stars')
    ])
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.student.user.username}'s feedback on {self.category}"

class MealPreference(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    breakfast = models.BooleanField(default=True)
    lunch = models.BooleanField(default=True)
    dinner = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        # Ensure a student can only have one preference per day
        unique_together = ('student', 'date')
        
    def __str__(self):
        return f"{self.student.user.username} - {self.date}"

class ChatMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    is_warden = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"
    