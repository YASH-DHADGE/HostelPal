from django import forms
from django.contrib.auth.models import User
from .models import Leave, Complaint, Student, Message, Attendance, MealPreference  # Assuming Leave model exists

class LeaveApplicationForm(forms.ModelForm):
    class Meta:
        model = Leave
        fields = ['from_date', 'to_date', 'reason']
        widgets = {
            'from_date': forms.DateInput(attrs={'type': 'date'}),
            'to_date': forms.DateInput(attrs={'type': 'date'}),
            'reason': forms.Textarea(attrs={'rows': 4}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        from_date = cleaned_data.get('from_date')
        to_date = cleaned_data.get('to_date')
        
        if from_date and to_date:
            if to_date < from_date:
                raise forms.ValidationError("End date cannot be before start date")
        
        return cleaned_data


class RegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput(), required=True)
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50, required=False)
    last_name = forms.CharField(max_length=50, required=False)
    room_number = forms.CharField(max_length=10, required=True)  # modified this line
    phone_number = forms.CharField(max_length=15, required=True)  # modified this line

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'room_number',
                  'phone_number']  # modified this line

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            student = Student.objects.create(
                user=user,
                first_name=self.cleaned_data.get('first_name'),
                last_name=self.cleaned_data.get('last_name'),
                room_number=self.cleaned_data['room_number'],
                phone_number=self.cleaned_data['phone_number'],
            )
        return user

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['complaint_type', 'description']
        labels = {
            'complaint_type': 'Complaint Type',
            'description': 'Description'
        }
        widgets = {
            'complaint_type': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']  # Or whatever fields you have in your Message model

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

class LeaveForm(forms.ModelForm):
    class Meta:
        model = Leave
        fields = ['from_date', 'to_date', 'reason']
        widgets = {
            'from_date': forms.DateInput(attrs={'type': 'date'}),
            'to_date': forms.DateInput(attrs={'type': 'date'}),
            'reason': forms.Textarea(attrs={'rows': 4}),
        }

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['student', 'date', 'status', 'check_in', 'check_out', 'comment']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'check_in': forms.TimeInput(attrs={'type': 'time'}),
            'check_out': forms.TimeInput(attrs={'type': 'time'}),
            'comment': forms.Textarea(attrs={'rows': 2}),
        }

class BulkAttendanceForm(forms.Form):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    
    def __init__(self, *args, **kwargs):
        students = kwargs.pop('students', None)
        super(BulkAttendanceForm, self).__init__(*args, **kwargs)
        
        if students:
            for student in students:
                self.fields[f'status_{student.id}'] = forms.ChoiceField(
                    choices=Attendance.ATTENDANCE_STATUS,
                    initial='present',
                    widget=forms.Select(attrs={'class': 'form-select'})
                )
                self.fields[f'comment_{student.id}'] = forms.CharField(
                    required=False,
                    widget=forms.Textarea(attrs={'rows': 1, 'class': 'form-control'})
                )

class MealPreferenceForm(forms.ModelForm):
    class Meta:
        model = MealPreference
        fields = ['date', 'breakfast', 'lunch', 'dinner']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
