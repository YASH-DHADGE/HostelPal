"""
URL configuration for HostelPal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.contrib.auth import views as auth_views

admin.site.site_header="HostelPal Warden Login"
admin.site.site_title="Welcome Warden"

admin.site.site_url="/warden"
admin.site.index_title="Hello Warden"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Home.urls')),
    # path('account/', include('Account.urls')),

    # Password Reset URLs
    path('password_reset/', 
         auth_views.PasswordResetView.as_view(template_name='password_reset.html'),
         name='password_reset'),
    
    path('password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'),
         name='password_reset_done'),
    
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),
         name='password_reset_confirm'),
    
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),
         name='password_reset_complete'),

    # Warden Password Reset URLs
    path('wardens/password_reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='warden/password_reset.html',
             email_template_name='warden/password_reset_email.html',
             success_url='/wardens/password_reset/done/'
         ),
         name='warden_password_reset'),
    
    path('wardens/password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='warden/password_reset_done.html'
         ),
         name='warden_password_reset_done'),
    
    path('wardens/reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='warden/password_reset_confirm.html',
             success_url='/wardens/reset/done/'
         ),
         name='warden_password_reset_confirm'),
    
    path('wardens/reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='warden/password_reset_complete.html'
         ),
         name='warden_password_reset_complete'),
]
