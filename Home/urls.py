from django.contrib import admin
from django.urls import path, include
from Home import views
from django.contrib.auth import views as auth_views
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required, user_passes_test
from Home.models import Notice

admin.site.site_header="HostelPal Warden Login"
admin.site.site_title="Welcome Warden"

admin.site.site_url="/wardens/dashboard/"
admin.site.index_title="Hello Warden"

urlpatterns = [
    path("warden/", admin.site.urls),
    path("", views.index, name='home'),
    path("account/", views.account, name='account'),
    path("attendance/", views.attendance, name='attendance'),
    path("chat/", views.student_chat, name='chat'),
    path("feedback/", views.feedback, name='feedback'),
    path("leave/", views.leave, name='leave'),
    path("leave-status/", views.leave_status, name='leave_status'),
    path("mess/", views.mess, name='mess'),
    path("notice/", views.notice, name='notice'),
    path("ticket/", views.ticket, name='ticket'),
    path('leave/apply/', views.leave_application, name='leave_application'),
    path("login/", auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path("logout/", auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
    path("password_change/", auth_views.PasswordChangeView.as_view(template_name='password_change.html'), name='password_change'),
    path("password_change/done/", auth_views.PasswordChangeDoneView.as_view(template_name='password_change_done.html'), name='password_change_done'),
    path("register/", views.register, name='register'),
    path("submit_complaint/",views.submit_complaint,name="submit_complaint"),
    path("view_complaint/",views.view_complaint,name="view_complaint"),
    path("store_chat/",views.store_chat,name="store_chat"),  
    path("pay_fees/", views.pay_fees, name='pay_fees'),
    path("update_today_meal/", views.update_today_meal, name='update_today_meal'),
]

# Add URL pattern for mess feedback submission
urlpatterns += [
    path("submit_mess_feedback/", views.submit_mess_feedback, name='submit_mess_feedback'),
]

# Warden interface URLs with updated paths
urlpatterns += [
    # Main warden pages
    path("wardens/login/", views.warden_login, name='warden_login'),
    path("wardens/dashboard/", views.warden_dashboard, name='warden_dashboard'),
    
    # Complaints management
    path("wardens/complaints/", views.warden_complaints, name='warden_complaints'),
    path("wardens/complaints/resolve/<int:complaint_id>/", views.resolve_complaint, name='resolve_complaint'),
    path("wardens/complaints/reply/<int:complaint_id>/", views.reply_complaint, name='reply_complaint'),
    
    # Leave applications
    path("wardens/leaves/", views.warden_leave_applications, name='warden_leave_applications'),
    path("wardens/leaves/approve/<int:leave_id>/", views.approve_leave, name='approve_leave'),
    path("wardens/leaves/reject/<int:leave_id>/", views.reject_leave, name='reject_leave'),
    path("wardens/leaves/view/<int:leave_id>/", views.view_leave, name='view_leave'),
    
    # Notice management
    path("wardens/notices/", views.manage_notices, name='manage_notices'),
    path("wardens/notices/create/", views.create_notice, name='create_notice'),
    path("wardens/notices/edit/<int:notice_id>/", views.edit_notice, name='edit_notice'),
    path("wardens/notices/delete/<int:notice_id>/", views.delete_notice, name='delete_notice'),
    
    # Attendance
    path("wardens/attendance/", views.manage_attendance, name='manage_attendance'),
    path("wardens/mark-attendance/", views.mark_attendance, name='mark_attendance'),
    path("wardens/bulk-mark-attendance/", views.bulk_mark_attendance, name='bulk_mark_attendance'),
    path("wardens/attendance-report/", views.attendance_report, name='attendance_report'),
    
    # Chat and feedback
    path("wardens/chat/", views.warden_chat, name='warden_chat'),
    path("wardens/chat/<int:student_id>/", views.warden_chat_with_student, name='warden_chat_with_student'),
    path("wardens/chat/send/<int:student_id>/", views.send_message, name='send_message'),
]

# Student meal preference URLs
urlpatterns += [
    path("meals/", views.meal_preferences, name='meal_preferences'),
    path("meals/update/", views.update_meal_preference, name='update_meal_preference'),
]

# You could also add warden meal management URLs
urlpatterns += [
    path("wardens/meals/", views.warden_meal_management, name='warden_meal_management'),
]

# Chat URLs
urlpatterns += [
    path('chat/', views.student_chat, name='chat'),
    path('api/messages/', views.get_messages, name='get_messages'),
]

# Leave application URLs
urlpatterns += [
    path('leave/', views.leave, name='leave'),
    path('leave/apply/', views.apply_leave, name='apply_leave'),
    path('leave/view/<int:leave_id>/', views.view_leave, name='view_leave'),
    path('leave/edit/<int:leave_id>/', views.edit_leave, name='edit_leave'),
    path('leave/delete/<int:leave_id>/', views.delete_leave, name='delete_leave'),
]

@login_required
@user_passes_test(views.is_warden)
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
            return redirect(reverse('manage_notices'))
        else:
            messages.error(request, 'Title and content are required.')
    
    return render(request, 'edit_notice.html', {'notice': notice})

urlpatterns += [
    path('attendance/', views.student_attendance, name='student_attendance'),
]
