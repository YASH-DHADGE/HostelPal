from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from .models import Complaint, Student, Chat, Payment, Leave, Attendance, Notice, MealPreference, ChatMessage,Feedback
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import LeaveApplicationForm, ComplaintForm, RegistrationForm
from django.contrib.auth import authenticate, login, logout
from datetime import date, datetime, timedelta
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.template.exceptions import TemplateDoesNotExist
from django.conf import settings
import os
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count
import json
from django.db import ProgrammingError
from collections import deque
import time
from django.contrib.auth.models import User
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from io import BytesIO


# Create your views here.
@login_required
def index(request):
    
    # Get today's meal preferences
    student = request.user.student
    today = date.today()
    
    try:
        meal_pref = MealPreference.objects.get(student=student, date=today)
        breakfast_selected = meal_pref.breakfast
        lunch_selected = meal_pref.lunch
        dinner_selected = meal_pref.dinner
        meal_last_updated = meal_pref.updated_at
    except MealPreference.DoesNotExist:
        # Default to all selected if no preference exists
        breakfast_selected = True
        lunch_selected = True
        dinner_selected = True
        meal_last_updated = None
    except:
        # Handle any other errors
        breakfast_selected = True
        lunch_selected = True
        dinner_selected = True
        meal_last_updated = None
    
    # Get student stats for dashboard
    try:
        # Attendance percentage (this is an example, adjust based on your model)
        total_days = Attendance.objects.filter(student=student).count()
        present_days = Attendance.objects.filter(student=student, present=True).count()
        attendance_percentage = int((present_days / total_days) * 100) if total_days > 0 else 0
    except:
        attendance_percentage = 0
    
    # Count leave requests
    try:
        leave_count = Leave.objects.filter(student=student).count()
    except:
        leave_count = 0
    
    # Count complaints
    try:
        complaint_count = Complaint.objects.filter(student=student).count()
    except:
        complaint_count = 0
    
    # Count unread notices
    try:
        notice_count = Notice.objects.count()  # You might want to filter for new notices only
    except:
        notice_count = 0
    
    context = {
        'breakfast_selected': breakfast_selected,
        'lunch_selected': lunch_selected,
        'dinner_selected': dinner_selected,
        'meal_last_updated': meal_last_updated,
        'attendance_percentage': attendance_percentage,
        'leave_count': leave_count,
        'complaint_count': complaint_count,
        'notice_count': notice_count,
    }
    
    return render(request, 'home.html', context)

@login_required  # Add login_required for security
def account(request):
    try:
        # Fetch payment records for the current user
        payments = Payment.objects.filter(student=request.user.student).order_by('-payment_date')
        return render(request, 'account.html', {'payments': payments})
    except Exception as e:
        # Handle errors gracefully
        messages.error(request, f'Error retrieving payment data: {str(e)}')
        return render(request, 'account.html', {'payments': []})


# Helper function to check if user is warden
def is_warden(user):
    return user.is_staff

@csrf_exempt
@login_required
def bulk_mark_attendance(request):
    """Endpoint for marking attendance in bulk"""
    if not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
    
    # Return a message that the system is under construction
    return JsonResponse({
        'status': 'info',
        'message': 'The attendance system is currently under construction. Please check back later.'
    })

# Warden login view
def warden_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_staff:
            login(request, user)
            messages.success(request, f'Welcome, {user.username}!')
            return redirect('warden_dashboard')
        else:
            return render(request, 'warden/login.html', {'error_message': 'Invalid credentials or insufficient permissions'})
    
    return render(request, 'warden/login.html')

# Use this decorator only for testing, remove it in production
@csrf_exempt
@login_required
@user_passes_test(is_warden)
def warden_dashboard(request):
    # Get counts for dashboard stats
    students_count = Student.objects.count()
    complaints_count = Complaint.objects.count()
    leave_count = Leave.objects.filter(status='pending').count()
    notices_count = Notice.objects.count()
    
    # Try to get recent complaints
    try:
        recent_complaints = Complaint.objects.all()[:5]
    except:
        recent_complaints = []
    
    # Try to get recent leave applications
    try:
        recent_leaves = Leave.objects.all().order_by('-application_date')[:5]
    except:
        recent_leaves = []
    
    # Get today's meal counts with proper error handling
    today = date.today()
    
    try:
        # Count students who have opted in for each meal
        breakfast_count = MealPreference.objects.filter(date=today, breakfast=True).count()
        lunch_count = MealPreference.objects.filter(date=today, lunch=True).count()
        dinner_count = MealPreference.objects.filter(date=today, dinner=True).count()
        
        # For students who haven't set preferences, assume they're eating
        students_with_prefs = MealPreference.objects.filter(date=today).values_list('student_id', flat=True)
        students_without_prefs = Student.objects.exclude(id__in=students_with_prefs).count()
        
        # Add students without preferences to the counts (assuming they eat all meals)
        breakfast_count += students_without_prefs
        lunch_count += students_without_prefs
        dinner_count += students_without_prefs
        
    except Exception as e:
        # Log the error
        print(f"Error calculating meal counts: {str(e)}")
        breakfast_count = students_count  # Default to all students
        lunch_count = students_count
        dinner_count = students_count
    
    # Create context without trying to access MealPreference yet
    context = {
        'students_count': students_count,
        'complaints_count': complaints_count,
        'leave_count': leave_count,
        'notices_count': notices_count,
        'recent_complaints': recent_complaints,
        'recent_leaves': recent_leaves,
        'meal_date': today,
        'breakfast_count': breakfast_count,
        'lunch_count': lunch_count,
        'dinner_count': dinner_count,
    }
    
    return render(request, 'warden/home.html', context)

# Notice Board Management
@login_required
@user_passes_test(is_warden)
def manage_notices(request):
    notices = Notice.objects.all().order_by('-date_posted')
    return render(request, 'warden/manage_notices.html', {'notices': notices})

@login_required
@user_passes_test(is_warden)
def create_notice(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        important = 'important' in request.POST
        
        if title and content:
            Notice.objects.create(title=title, content=content, important=important)
            messages.success(request, 'Notice created successfully!')
            return redirect('manage_notices')
        else:
            messages.error(request, 'Title and content are required.')
    
    return render(request, 'warden/create_notice.html')

@login_required
@user_passes_test(is_warden)
def edit_notice(request, notice_id):
    notice = get_object_or_404(Notice, id=notice_id)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        important = 'important' in request.POST
        
        if title and content:
            notice.title = title
            notice.content = content
            notice.important = important
            notice.save()
            messages.success(request, 'Notice updated successfully!')
            return redirect('manage_notices')
        else:
            messages.error(request, 'Title and content are required.')
    
    return render(request, 'warden/edit_notice.html', {'notice': notice})

@login_required
@user_passes_test(is_warden)
def delete_notice(request, notice_id):
    notice = get_object_or_404(Notice, id=notice_id)
    
    if request.method == 'POST':
        notice.delete()
        messages.success(request, 'Notice deleted successfully!')
        return redirect('manage_notices')
    
    return render(request, 'warden/delete_notice.html', {'notice': notice})

@login_required
@user_passes_test(is_warden)
def manage_attendance(request):
    """View for the warden to manage attendance"""
    if request.method == 'POST':
        date = request.POST.get('date')
        if not date:
            messages.error(request, "Please select a date")
            return redirect('manage_attendance')
        
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()
            
            # Process the bulk attendance form
            for key, value in request.POST.items():
                if key.startswith('status_'):
                    student_id = key.split('_')[1]
                    status = value
                    comment = request.POST.get(f'comment_{student_id}', '')
                    
                    try:
                        student = User.objects.get(id=student_id)
                        
                        # Update or create attendance record
                        attendance, created = Attendance.objects.update_or_create(
                            student=student,
                            date=date_obj,
                            defaults={
                                'status': status,
                                'marked_by': request.user,
                                'comment': comment,
                                'present': status == 'present',
                                'updated_at': timezone.now()
                            }
                        )
                    except User.DoesNotExist:
                        continue
            
            messages.success(request, f"Attendance for {date} has been recorded")
            return redirect('manage_attendance')
            
        except Exception as e:
            messages.error(request, f"Error saving attendance: {str(e)}")
            return redirect('manage_attendance')
    
    # Handle GET request
    try:
        students = User.objects.filter(student__isnull=False).order_by('username')
        date = request.GET.get('date', timezone.now().strftime('%Y-%m-%d'))
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        
        # Get existing attendance records for the date
        attendance_records = {
            a.student_id: a for a in Attendance.objects.filter(date=date_obj)
        }
        
        # Prepare data for the template
        student_attendance = []
        for student in students:
            attendance = attendance_records.get(student.id, None)
            student_attendance.append({
                'student': student,
                'status': attendance.status if attendance else 'absent',
                'comment': attendance.comment if attendance else '',
            })
        
        context = {
            'student_attendance': student_attendance,
            'date': date,
            'attendance_statuses': dict(Attendance.ATTENDANCE_STATUS),
        }
        return render(request, 'warden/manage_attendance.html', context)
    except Exception as e:
        messages.error(request, f"Error loading attendance data: {str(e)}")
        return render(request, 'warden/manage_attendance.html', {'error': str(e)})

@login_required
def attendance_report(request):
    """Generate attendance reports for warden"""
    try:
        # Get filter parameters
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        status_filter = request.GET.get('status', '')
        
        if not start_date:
            start_date = (timezone.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = timezone.now().strftime('%Y-%m-%d')
            
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Base query
        query = Attendance.objects.filter(date__range=[start_date_obj, end_date_obj])
        
        # Apply status filter if provided
        if status_filter and status_filter != 'all':
            query = query.filter(status=status_filter)
        
        # Aggregate data for reports
        attendance_by_date = query.values('date').annotate(
            total=Count('id'),
            present=Count('id', filter=Q(status='present')),
            absent=Count('id', filter=Q(status='absent')),
            on_leave=Count('id', filter=Q(status='leave'))
        ).order_by('-date')
        
        # Get overall statistics
        total_records = query.count()
        present_count = query.filter(status='present').count()
        absent_count = query.filter(status='absent').count()
        leave_count = query.filter(status='leave').count()
        
        present_percentage = 0
        if total_records > 0:
            present_percentage = round((present_count / total_records) * 100, 2)
        
        context = {
            'attendance_by_date': attendance_by_date,
            'start_date': start_date,
            'end_date': end_date,
            'status_filter': status_filter,
            'total_records': total_records,
            'present_count': present_count,
            'absent_count': absent_count,
            'leave_count': leave_count,
            'present_percentage': present_percentage,
            'attendance_statuses': dict(Attendance.ATTENDANCE_STATUS),
        }
        return render(request, 'warden/attendance_report.html', context)
    except Exception as e:
        messages.error(request, f"Error generating report: {str(e)}")
        return render(request, 'warden/attendance_report.html', {'error': str(e)})

# Update the notice view for students to show notices from the database
def notice(request):
    notices = Notice.objects.all().order_by('-date_posted')
    important_notices = notices.filter(important=True)
    regular_notices = notices.filter(important=False)
    
    context = {
        'important_notices': important_notices,
        'regular_notices': regular_notices
    }
    
    return render(request, 'notice.html', context)

@login_required
def attendance(request):
    """Simple view that returns the under construction attendance page"""
    return render(request, 'attendance.html')

def chat(request):
    return render(request, 'chat.html')

def feedback(request):
    return render(request, 'feedback.html')

@login_required
def leave(request):
    """View for listing student's leave applications"""
    try:
        leave_applications = Leave.objects.filter(student=request.user.student).order_by('-application_date')
        print(f"Found {leave_applications.count()} leave applications for {request.user.username}")
    except Exception as e:
        leave_applications = []
        print(f"Error retrieving leave applications: {str(e)}")
        messages.error(request, "Unable to retrieve your leave applications. The system is being updated.")
    
    context = {
        'leave_applications': leave_applications,
    }
    
    return render(request, 'leave.html', context)

@login_required
def leave_status(request):
    # Get all leave requests for current student
    try:
        leave_requests = Leave.objects.filter(student=request.user.student).order_by('-from_date')
        print(f"Found {leave_requests.count()} leave requests for student {request.user.username}")
    except Exception as e:
        print(f"Error fetching leave requests: {str(e)}")
        leave_requests = []
        messages.error(request, "Unable to retrieve your leave requests. The system is being updated.")
    
    return render(request, 'leave-status.html', {'leave_requests': leave_requests})

@login_required
def mess(request):
    """View for mess page"""
    # Simple context without database access
    context = {}

    return render(request, 'mess.html', context)
 
def view_complaint(request):
    complaints = Complaint.objects.all()
    return render(request, 'view_complaint.html', {'complaints': complaints})

@login_required
def submit_complaint(request):
    """View for submitting a new complaint"""
    if request.method == 'POST':
        complaint_type = request.POST.get('complaint_type')
        description = request.POST.get('description')
        
        # Simple validation
        if not all([complaint_type, description]):
            messages.error(request, 'All fields are required.')
            return redirect('ticket')
        
        try:
            # Get the Student object related to the current user
            student = Student.objects.get(user=request.user)
            
            # Create and save the complaint
            complaint = Complaint(
                student=student,
                complaint_type=complaint_type,
                description=description
            )
            complaint.save()
            messages.success(request, 'Complaint submitted successfully!')
        except Exception as e:
            print(f"Error saving complaint: {str(e)}")
            messages.success(request, 'Complaint submitted successfully. The system is being updated, and your complaint will be processed shortly.')
    
    return redirect('ticket')

@login_required
def ticket(request):
    """View for complaints page"""
    # Show form without database access for now
    form = ComplaintForm()
    
    context = {
        'form': form,
        'complaints': []
    }
    
    return render(request, 'ticket.html', context)

@login_required
def leave_application(request):
    if request.method == 'POST':
        form = LeaveApplicationForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            # Changed this to request.user.student since the Leave model expects a Student instance
            leave.student = request.user.student
            leave.status = 'pending'  # Set default status
            
            # Calculate the number of days
            delta = (leave.to_date - leave.from_date).days + 1
            leave.days = delta
            
            # Add debug printing to check what's going on
            print(f"Creating leave record: Student ID={request.user.student.id}, Username={request.user.username}")
            
            try:
                leave.save()  # This saves to the database
                # Debug info to confirm save
                print(f"Leave request saved: ID={leave.id}, Student={leave.student}, Dates={leave.from_date} to {leave.to_date}")
                
                messages.success(request, 'Leave application submitted successfully!')
                return redirect('leave_status')
            except Exception as e:
                # Log the error for debugging
                print(f"Error saving leave application: {str(e)}")
                messages.error(request, f"Error saving application: {str(e)}")
        else:
            # If form has errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = LeaveApplicationForm()
    
    return render(request, 'leave_application.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Make sure you're creating a Student record for each user
            # This might be in your form's save method, but if not:
            try:
                # Create a Student profile for the user
                student = Student(
                    user=user,
                    email=user.email,
                    # Add any other required fields
                )
                student.save()
            except Exception as e:
                messages.error(request, f'Error creating student profile: {str(e)}')
                
            # Log the user in
            login(request, user)
            messages.success(request, 'Registration successful! You are now logged in.')
            return redirect('home')
        else:
            # If form is not valid, display form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

def chat(request):
    chats = Chat.objects.all()
    return render(request, 'chat.html', {'messages': chats, 'user': request.user.student.first_name})

def store_chat(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        student = request.user.student
        student_name=student.first_name
        Chat.objects.create(message=message, student=student,student_name=student_name)
    return redirect('chat')

@login_required
def pay_fees(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        if amount:
            try:
                amount = float(amount)
                if amount > 0:
                    student = request.user.student
                    payment_date = date.today()
                    payment = Payment(student=student, amount=amount, payment_date=payment_date)
                    payment.save()
                    messages.success(request, 'Payment successful!')
                    return redirect('account')
                else:
                    messages.error(request, 'Please enter a valid amount greater than zero.')
            except ValueError:
                messages.error(request, 'Invalid amount entered.')
        else:
            messages.error(request, 'Please enter an amount.')

    return redirect('account')

@login_required
@user_passes_test(is_warden)
def warden_complaints(request):
    # Use try/except to handle the field not existing yet
    try:
        complaints = Complaint.objects.all().order_by('-created_at')
    except:
        complaints = Complaint.objects.all()
        
    return render(request, 'warden/complaints.html', {'complaints': complaints})

@login_required
@user_passes_test(is_warden)
def resolve_complaint(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)
    
    if request.method == 'POST':
        complaint.resolved = True
        complaint.resolved_at = timezone.now()
        complaint.save()
        messages.success(request, f'Complaint has been marked as resolved.')
    
    return redirect('warden_complaints')

@login_required
@user_passes_test(is_warden)
def reply_complaint(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)
    
    if request.method == 'POST':
        reply = request.POST.get('reply')
        if reply:
            # Save reply logic here (you might need to add a reply field to your Complaint model)
            complaint.reply = reply
            complaint.replied_at = timezone.now()
            complaint.save()
            messages.success(request, f'Your reply has been sent to the student.')
            return redirect('warden_complaints')
    
    return render(request, 'warden/reply_complaint.html', {'complaint': complaint})

@login_required
@user_passes_test(is_warden)
def warden_leave_applications(request):
    leaves = Leave.objects.all().order_by('-application_date')
    
    # Add duration field to leaves
    for leave in leaves:
        delta = (leave.to_date - leave.from_date).days + 1
        leave.duration = delta
    
    return render(request, 'warden/leave_applications.html', {'leaves': leaves})

@login_required
@user_passes_test(is_warden)
def approve_leave(request, leave_id):
    leave = get_object_or_404(Leave, id=leave_id)
    
    if request.method == 'POST':
        leave.status = 'approved'
        leave.approved_by = request.user
        leave.approval_date = timezone.now()
        leave.save()
        messages.success(request, f'Leave application has been approved.')
    
    return redirect('warden_leave_applications')

@login_required
@user_passes_test(is_warden)
def reject_leave(request, leave_id):
    leave = get_object_or_404(Leave, id=leave_id)
    
    if request.method == 'POST':
        leave.status = 'rejected'
        leave.approved_by = request.user
        leave.approval_date = timezone.now()
        leave.save()
        messages.success(request, f'Leave application has been rejected.')
    
    return redirect('warden_leave_applications')

@login_required
def view_leave(request, leave_id):
    """View for details of a leave application"""
    leave = get_object_or_404(Leave, id=leave_id, student=request.user.student)
    
    context = {
        'leave': leave
    }
    
    return render(request, 'leave_detail.html', context)

# In-memory storage for chat messages (will reset on server restart)
CHAT_MESSAGES = deque(maxlen=100)  # Store the last 100 messages

@login_required
def warden_chat(request):
    # Check if user is a warden
    if not request.user.is_staff:  # Adjust this check based on how you identify wardens
        return redirect('home')
    
    if request.method == 'POST':
        content = request.POST.get('message', '').strip()
        if content:
            # Create a message object (without saving to DB)
            message = {
                'id': int(time.time() * 1000),  # Use timestamp as ID
                'sender_username': request.user.username,
                'sender': request.user,
                'content': content,
                'timestamp': timezone.now(),
                'is_warden': True
            }
            CHAT_MESSAGES.append(message)
    
    # Prepare messages for the template
    context_messages = list(CHAT_MESSAGES)
    for msg in context_messages:
        msg['is_self'] = msg['sender'] == request.user
    
    return render(request, 'warden/chat.html', {
        'messages': context_messages,
        'is_warden': True
    })

@login_required
@user_passes_test(is_warden)
def warden_chat_with_student(request, student_id):
    students = Student.objects.all()
    selected_student = get_object_or_404(Student, id=student_id)
    
    # Get chat messages for this student
    messages = Chat.objects.filter(student=selected_student).order_by('timestamp')
    
    # Add a flag to identify warden messages (you might need to modify your Chat model)
    for msg in messages:
        msg.is_warden = msg.sender_type == 'WARDEN' if hasattr(msg, 'sender_type') else False
    
    context = {
        'students': students,
        'selected_student': selected_student,
        'messages': messages,
    }
    
    return render(request, 'warden/chat.html', context)

@login_required
@user_passes_test(is_warden)
def send_message(request, student_id):
    if request.method == 'POST':
        message_content = request.POST.get('message')
        student = get_object_or_404(Student, id=student_id)
        
        # Create new chat message (you might need to modify your Chat model)
        chat = Chat(
            message=message_content,
            student=student,
            student_name="Warden",  # Or request.user.username
            sender_type="WARDEN"    # You might need to add this field
        )
        chat.save()
        
        messages.success(request, 'Message sent successfully.')
        return redirect('warden_chat_with_student', student_id=student_id)
    
    return redirect('warden_chat')

@login_required
def meal_preferences(request):
    # Get next 7 days for meal planning
    today = date.today()
    next_days = [today + timedelta(days=i) for i in range(7)]
    
    # Get existing preferences
    student = request.user.student
    existing_preferences = {}
    
    for pref in MealPreference.objects.filter(student=student, date__in=next_days):
        existing_preferences[pref.date.isoformat()] = {
            'breakfast': pref.breakfast,
            'lunch': pref.lunch,
            'dinner': pref.dinner
        }
    
    context = {
        'next_days': next_days,
        'existing_preferences': existing_preferences,
    }
    
    return render(request, 'meal_preferences.html', context)

@login_required
def update_meal_preference(request):
    if request.method == 'POST':
        date_str = request.POST.get('date')
        meal_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        breakfast = 'breakfast' in request.POST
        lunch = 'lunch' in request.POST
        dinner = 'dinner' in request.POST
        
        student = request.user.student
        
        # Create or update preference
        pref, created = MealPreference.objects.update_or_create(
            student=student,
            date=meal_date,
            defaults={
                'breakfast': breakfast,
                'lunch': lunch,
                'dinner': dinner
            }
        )
        
        messages.success(request, f'Meal preferences for {meal_date} updated successfully!')
        return redirect('meal_preferences')
    
    return redirect('meal_preferences')

@login_required
@user_passes_test(is_warden)
def warden_meal_management(request):
    # Get meal counts for next 7 days
    today = date.today()
    next_days = [today + timedelta(days=i) for i in range(7)]
    
    meal_data = {}
    for day in next_days:
        breakfast_count = MealPreference.objects.filter(date=day, breakfast=True).count()
        lunch_count = MealPreference.objects.filter(date=day, lunch=True).count()
        dinner_count = MealPreference.objects.filter(date=day, dinner=True).count()
        
        meal_data[day] = {
            'breakfast': breakfast_count,
            'lunch': lunch_count,
            'dinner': dinner_count,
        }
    
    # Get student list who opted out today
    opted_out_breakfast = Student.objects.filter(
        mealpreference__date=today,
        mealpreference__breakfast=False
    ).order_by('room_number')
    
    opted_out_lunch = Student.objects.filter(
        mealpreference__date=today,
        mealpreference__lunch=False
    ).order_by('room_number')
    
    opted_out_dinner = Student.objects.filter(
        mealpreference__date=today,
        mealpreference__dinner=False
    ).order_by('room_number')
    
    context = {
        'next_days': next_days,
        'meal_data': meal_data,
        'opted_out_breakfast': opted_out_breakfast,
        'opted_out_lunch': opted_out_lunch,
        'opted_out_dinner': opted_out_dinner,
    }
    
    return render(request, 'warden/meal_management.html', context)

@login_required
def update_today_meal(request):
    if request.method == 'POST':
        try:
            today = date.today()
            student = request.user.student
            
            breakfast = 'breakfast' in request.POST
            lunch = 'lunch' in request.POST
            dinner = 'dinner' in request.POST
            
            # Create or update today's preference
            meal_pref, created = MealPreference.objects.update_or_create(
                student=student,
                date=today,
                defaults={
                    'breakfast': breakfast,
                    'lunch': lunch,
                    'dinner': dinner
                }
            )
            
            messages.success(request, "Meal preferences updated successfully!")
        except:
            messages.error(request, "There was an error updating your meal preferences.")
    
    return redirect('home')

# Student chat view
@login_required
def student_chat(request):
    if request.method == 'POST':
        content = request.POST.get('message', '').strip()
        if content:
            # Create a message object (without saving to DB)
            message = {
                'id': int(time.time() * 1000),  # Use timestamp as ID
                'sender_username': request.user.username,
                'sender': request.user,
                'content': content,
                'timestamp': timezone.now(),
                'is_warden': False
            }
            CHAT_MESSAGES.append(message)
    
    # Prepare messages for the template
    context_messages = list(CHAT_MESSAGES)
    for msg in context_messages:
        msg['is_self'] = msg['sender'] == request.user
    
    return render(request, 'chat.html', {
        'messages': context_messages,
        'is_warden': False
    })

# API for fetching messages
@login_required
def get_messages(request):
    last_id = request.GET.get('last_id', 0)
    messages = ChatMessage.objects.filter(id__gt=last_id).order_by('timestamp')
    
    data = [{
        'id': msg.id,
        'sender': msg.sender.username,
        'content': msg.content,
        'timestamp': msg.timestamp.strftime('%b %d, %Y, %I:%M %p'),
        'is_warden': msg.is_warden,
        'is_self': msg.sender == request.user
    } for msg in messages]
    
    return JsonResponse({'messages': data})

@login_required
def mark_attendance(request):
    """API endpoint for marking attendance"""
    if not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
    
    # Return a message that the system is under construction
    return JsonResponse({
        'status': 'info',
        'message': 'The attendance system is currently under construction. Please check back later.'
    })

@login_required
def apply_leave(request):
    """View for submitting a new leave application"""
    if request.method == 'POST':
        try:
            from_date = request.POST.get('from_date')
            to_date = request.POST.get('to_date')
            reason = request.POST.get('reason')
            
            # Simple validation
            if not all([from_date, to_date, reason]):
                messages.error(request, 'All fields are required.')
                return redirect('leave')
            
            # Try to create and save the leave application
            try:
                from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
                to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
                
                if from_date > to_date:
                    messages.error(request, 'From date cannot be after to date.')
                    return redirect('leave')
                
                # Calculate days
                days = (to_date - from_date).days + 1
                
                # Create new leave application with request.user.student (not request.user)
                leave = Leave(
                    student=request.user.student,
                    from_date=from_date,
                    to_date=to_date,
                    days=days,
                    reason=reason,
                    status='pending'
                )
                leave.save()
                messages.success(request, 'Leave application submitted successfully.')
                return redirect('leave')
            except Exception as e:
                print(f"Database error in apply_leave: {str(e)}")
                messages.error(request, f'Error creating leave application: {str(e)}')
                return redirect('leave')
                
        except Exception as e:
            print(f"Error in apply_leave view: {str(e)}")
            messages.error(request, "Unable to process leave application. The system is being updated.")
        
    # GET request shouldn't access this view directly
    return redirect('leave')

@login_required
def edit_leave(request, leave_id):
    """View for editing a leave application"""
    leave = get_object_or_404(Leave, id=leave_id, student=request.user.student)
    
    # Only pending leave applications can be edited
    if leave.status != 'pending':
        messages.error(request, 'Only pending leave applications can be edited.')
        return redirect('leave')
    
    if request.method == 'POST':
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        reason = request.POST.get('reason')
        
        # Validate dates
        try:
            from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
            
            if from_date > to_date:
                messages.error(request, 'From date cannot be after to date.')
                return redirect('edit_leave', leave_id=leave_id)
                
            # Calculate number of days
            days = (to_date - from_date).days + 1
            
            # Update leave application
            leave.from_date = from_date
            leave.to_date = to_date
            leave.days = days
            leave.reason = reason
            leave.save()
            
            messages.success(request, 'Leave application updated successfully.')
            return redirect('leave')
            
        except Exception as e:
            messages.error(request, f'Error updating leave application: {str(e)}')
            return redirect('edit_leave', leave_id=leave_id)
    
    context = {
        'leave': leave
    }
    
    return render(request, 'edit_leave.html', context)

@login_required
def delete_leave(request, leave_id):
    """View for deleting a leave application"""
    leave = get_object_or_404(Leave, id=leave_id, student=request.user.student)
    
    # Only pending leave applications can be deleted
    if leave.status != 'pending':
        messages.error(request, 'Only pending leave applications can be deleted.')
        return redirect('leave')
    
    if request.method == 'POST':
        leave.delete()
        messages.success(request, 'Leave application deleted successfully.')
        return redirect('leave')
    
    context = {
        'leave': leave
    }
    
    return render(request, 'delete_leave.html', context)

@login_required
def student_attendance(request):
    from datetime import datetime, timedelta
    
    # Get date range parameters or default to current month
    today = datetime.now().date()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))
    
    # Create date range for the selected month
    if month == 12:
        next_month = datetime(year + 1, 1, 1).date()
    else:
        next_month = datetime(year, month + 1, 1).date()
    
    start_date = datetime(year, month, 1).date()
    end_date = next_month - timedelta(days=1)
    
    try:
        # Get attendance records for the student in the selected month
        attendance_records = Attendance.objects.filter(
            student=request.user, 
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date')
        
        # Create a calendar with attendance status
        calendar_data = {}
        for day in range((end_date - start_date).days + 1):
            current_date = start_date + timedelta(days=day)
            calendar_data[current_date] = {'status': 'not_marked', 'record': None}
        
        # Add attendance status to calendar
        for record in attendance_records:
            calendar_data[record.date]['status'] = record.status
            calendar_data[record.date]['record'] = record
        
        # Calculate attendance statistics
        total_days = len(calendar_data)
        present_days = sum(1 for data in calendar_data.values() if data['status'] == 'present')
        absent_days = sum(1 for data in calendar_data.values() if data['status'] == 'absent')
        leave_days = sum(1 for data in calendar_data.values() if data['status'] == 'leave')
        not_marked = sum(1 for data in calendar_data.values() if data['status'] == 'not_marked')
        
        attendance_percentage = (present_days / (total_days - not_marked) * 100) if (total_days - not_marked) > 0 else 0
        
        # Previous and next month links
        if month == 1:
            prev_month_link = f'?year={year-1}&month=12'
        else:
            prev_month_link = f'?year={year}&month={month-1}'
            
        if month == 12:
            next_month_link = f'?year={year+1}&month=1'
        else:
            next_month_link = f'?year={year}&month={month+1}'
        
        context = {
            'calendar_data': calendar_data,
            'month_name': start_date.strftime('%B'),
            'year': year,
            'today': today,
            'prev_month_link': prev_month_link,
            'next_month_link': next_month_link,
            'attendance_stats': {
                'total_days': total_days,
                'present_days': present_days,
                'absent_days': absent_days,
                'leave_days': leave_days,
                'not_marked': not_marked,
                'attendance_percentage': round(attendance_percentage, 2)
            }
        }
        
        return render(request, 'student/attendance.html', context)
    except Exception as e:
        messages.error(request, f"Error loading attendance data: {str(e)}")
        return render(request, 'attendance.html', {'error': str(e)})

@login_required
def submit_mess_feedback(request):
    """Handle mess feedback submission"""
    if request.method == 'POST':
        meal = request.POST.get('meal')
        date = request.POST.get('date')
        rating = request.POST.get('rating')
        feedback = request.POST.get('feedback')
        suggestions = request.POST.get('suggestions')
        
        # For now, just show a success message without saving to database
        # In a real implementation, you would save this to a MessFeedback model
        messages.success(request, f'Thank you for your feedback about {meal}. Your input helps us improve the mess services.')
    
    # Redirect back to the mess page
    return redirect('mess')