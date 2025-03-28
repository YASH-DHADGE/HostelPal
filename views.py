from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import connection

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        
        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists')
            else:
                user = User.objects.create_user(username=username, password=password1)
                user.save()
                messages.success(request, 'Account created successfully')
                return redirect('login')
        else:
            messages.error(request, 'Passwords do not match')
    
    return render(request, 'register.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to the home page
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'login.html')

def home(request):
    return render(request, 'home.html')

def raw_sql_example(request):
    # Example of a raw SQL query to create a user
    with connection.cursor() as cursor:
        cursor.execute("INSERT INTO auth_user (username, password) VALUES (%s, %s)", ['john', 'password123'])

    # Example of a raw SQL query to retrieve a user
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM auth_user WHERE username = %s", ['john'])
        row = cursor.fetchone()
        user_data = {
            'id': row[0],
            'username': row[1],
            'password': row[2],
            # ...other fields...
        }

    # Example of a raw SQL query to update a user
    with connection.cursor() as cursor:
        cursor.execute("UPDATE auth_user SET email = %s WHERE username = %s", ['john@example.com', 'john'])

    # Example of a raw SQL query to delete a user
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM auth_user WHERE username = %s", ['john'])

    return render(request, 'raw_sql_example.html', {'user_data': user_data})



