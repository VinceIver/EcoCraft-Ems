from django.shortcuts import render, get_object_or_404, reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from .models import Employee, Comment, EmployeeAddress, Attendance
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required, permission_required
from datetime import datetime, timedelta 
import calendar
from .forms import CustomUserCreationForm

def index(request): 
    employee_list = Employee.objects.all().order_by('-id')
    paginator = Paginator(employee_list, 6)

    page_number = request.GET.get('page')

    employee_list = paginator.get_page(page_number)
    return render(request, 'users/index.html', {'page_obj': employee_list})
   

@login_required(login_url='/users/login')
@permission_required('users.add_employee', login_url='/users/login')
def add(request):
    return render(request, 'users/add.html')

def search(request):
    term = request.GET.get('search', '')
    employee_list = Employee.objects.filter( Q(emp_fname__icontains=term) | Q(emp_lname__icontains=term)).order_by('-id')

    paginator = Paginator(employee_list, 6)

    page_number = request.GET.get('page')

    employee_list = paginator.get_page(page_number)
    return render(request, 'users/index.html', {'page_obj': employee_list})


def calculate_salary(hours_worked, hourly_rate):
    # Define your salary calculation logic here based on hours_worked and hourly_rate
    return hours_worked * hourly_rate

from django.http import HttpResponseForbidden


def processadd(request):
    fname = request.POST.get('fname')
    lname = request.POST.get('lname')
    email = request.POST.get('email')
    hours_worked = float(request.POST.get('hours_worked'))
    hourly_rate = float(request.POST.get('hourly_rate'))
    position = request.POST.get('position')
    contact_number = request.POST.get('contact_number')

    birthday_str = request.POST.get('birthday')
    birthday = datetime.strptime(birthday_str, '%Y-%m-%d').date() if birthday_str else None

    if request.FILES.get('image'):
        employee_pic = request.FILES.get('image')
    else:
        employee_pic = 'profile_pic/image.jpg'

    try:
        n = Employee.objects.get(emp_email=email)
        return render(request, 'users/add.html', {'error_message': "Duplicated email: " + email})

    except ObjectDoesNotExist:
        calculated_salary = calculate_salary(hours_worked, hourly_rate)

        employee = Employee.objects.create(
            emp_email=email, emp_fname=fname, emp_lname=lname,
            emp_position=position, emp_image=employee_pic,
            salary=calculated_salary, contact_number=contact_number,
            birthday=birthday  # Include the birthday field
        )
        employee.save()

        address = EmployeeAddress.objects.create(
            employee=employee,
            street_address=request.POST.get('street_address'),
            city=request.POST.get('city'),
            state=request.POST.get('state'),
            zip_code=request.POST.get('zip_code'),
        )
        address.save()

        return HttpResponseRedirect('/users')


@login_required(login_url='/users/login')
@permission_required('users.change_employee', login_url='/users/login')
def detail(request, profile_id):
    try:
        employee = Employee.objects.get(pk=profile_id)
        comments = Comment.objects.filter(employee_id=profile_id)
        comments_count = Comment.objects.filter(employee_id=profile_id).count()

        # Get the start date (Monday) of the current week
        today = datetime.today()
        start_of_week = today - timedelta(days=today.weekday())

        # Generate dates for the current week (Monday to Sunday)
        week_dates = [(start_of_week + timedelta(days=i)).strftime('%b. %d, %Y') for i in range(7)]

        # Fetch attendance data for the employee
        attendance_days = Attendance.objects.filter(employee=employee)

    except Employee.DoesNotExist:
        raise Http404("Profile does not exist")

    return render(request, 'users/detail.html', {'employee': employee, 'comments': comments, 'comments_count': comments_count, 'attendance_days': attendance_days, 'week_dates': week_dates})

def delete(request, profile_id):
    Employee.objects.filter(id=profile_id).delete()
    return HttpResponseRedirect('/users')
@login_required(login_url='/users/login')
@permission_required('users.change_employee', login_url='/users/login')
def edit(request, profile_id):
    try:
        employee = Employee.objects.get(pk=profile_id)  
    except Employee.DoesNotExist:
        raise Http404("profile does not exist")
    return render(request, 'users/edit.html', {'employee' : employee})

def processedit(request, profile_id):
    employee = get_object_or_404(Employee, pk=profile_id)
    profile_pic = request.FILES.get('image')

    try:
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        position = request.POST.get('position')
        hours_worked = float(request.POST.get('hours_worked'))
        hourly_rate = float(request.POST.get('hourly_rate'))
        contact_number = request.POST.get('contact_number')
        street_address = request.POST.get('street_address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')
        birthday = request.POST.get('birthday')
        status = request.POST.get('status', 'active')  # Add this line to get the status field

    except (KeyError, Employee.DoesNotExist):
        return render(request, 'users/detail.html', {'employee': employee, 'error_message': "Problem Updating Records"})
    else:
        # Convert the birthday string to a datetime object
        if birthday:
            birthday = datetime.strptime(birthday, '%Y-%m-%d').date()

        # Calculate the salary based on the formula
        calculated_salary = calculate_salary(hours_worked, hourly_rate)

        # Update the Employee object with the calculated salary, birthday, and status
        employee.emp_fname = fname
        employee.emp_lname = lname
        employee.emp_email = email
        employee.emp_position = position
        employee.salary = calculated_salary
        employee.contact_number = contact_number
        employee.birthday = birthday
        employee.status = status  # Set the status

        if profile_pic:
            employee.emp_image = profile_pic

        employee.save()

        # Update the EmployeeAddress object
        address, created = EmployeeAddress.objects.get_or_create(employee=employee)
        address.street_address = street_address
        address.city = city
        address.state = state
        address.zip_code = zip_code
        address.save()

        return HttpResponseRedirect(reverse('employee:detail', args=(profile_id,)))


    
def loginview(request):
    return render(request, 'users/login.html')

def process(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    
    user = authenticate(username = username, password = password)
    if user is not None:
        login(request, user)
        return HttpResponseRedirect('/users')
    else:
        return render (request, 'users/login.html', {'error_message': "Login Failed"})
    
def processlogout(request):
    logout(request)
    return HttpResponseRedirect('/users/login')

def addcomment(request):
    comment_text = request.POST.get('comment')
    employee_id = request.POST.get('employee_id')
    name = request.POST.get('name')
    email = request.POST.get('email')

    comment = Comment.objects.create(employee_id=employee_id, body=comment_text, name=name, email=email)
    comment.save()
    return HttpResponseRedirect(reverse('employee:detail', args=(employee_id, )))


def update_attendance(request, profile_id):
    employee = get_object_or_404(Employee, pk=profile_id)

    if request.method == 'POST':
        attendance_dates = request.POST.getlist('attendance_dates')

        # Update or create attendance records
        for date_str in attendance_dates:
            date = datetime.strptime(date_str, '%b. %d, %Y').date()
            attendance, created = Attendance.objects.get_or_create(employee=employee, date=date)
            attendance.attended = True  # You might have another way to determine attendance
            attendance.save()

    return HttpResponseRedirect(reverse('employee:detail', args=(profile_id,)))

def get_status_display(self):
    return dict(Employee.STATUS_CHOICES)[self.status]
def on_leave(request):
    # Retrieve the list of employees on leave
    employees_on_leave = Employee.objects.filter(status='on_leave')

    # Paginate the employees, with 6 employees per page
    paginator = Paginator(employees_on_leave, 6)
    page_number = request.GET.get('page')

    try:
        employees_on_leave = paginator.page(page_number)
    except PageNotAnInteger:
        employees_on_leave = paginator.page(1)
    except EmptyPage:
        employees_on_leave = paginator.page(paginator.num_pages)

    context = {
        'employees_on_leave': employees_on_leave
    }

    return render(request, 'users/on_leave.html', context)

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

@login_required(login_url='/users/login')
@permission_required('users.add_employee', login_url='/users/login')
def attendances(request):
    all_employees = Employee.objects.all()
    selected_employee_id = request.GET.get('employee_id')

    if selected_employee_id:
        selected_employee = get_object_or_404(Employee, id=selected_employee_id)
        filtered_attendance_days = Attendance.objects.filter(employee=selected_employee)
    else:
        selected_employee = None
        filtered_attendance_days = Attendance.objects.all()

    # Paginate the attendance data, with 10 entries per page (adjust as needed)
    paginator = Paginator(filtered_attendance_days, 10)
    page = request.GET.get('page')

    try:
        filtered_attendance_days = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        filtered_attendance_days = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g., 9999), deliver last page of results.
        filtered_attendance_days = paginator.page(paginator.num_pages)

    context = {
        'all_employees': all_employees,
        'selected_employee': selected_employee,
        'filtered_attendance_days': filtered_attendance_days,
    }

    return render(request, 'users/attendance.html', context)

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            user.user_permissions.clear()

    
            login(request, user)  # Automatically log in the user after signup
            return HttpResponseRedirect('/users')  # Redirect to the desired page after signup
    else:
        form = CustomUserCreationForm()

    return render(request, 'users/signup.html', {'form': form})