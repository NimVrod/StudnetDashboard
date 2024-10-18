from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.models import User

from StudentDashboard.models import Student, CourseStudent, Course


def home(request):
    courses = [
        {
            'title': 'Elementy Elektroniczne EiT 23/24',
            'category': 'Elektronika i Telekomunikacja',
            'progress': 11,
            'image_url': '/static/images/course1.jpg',
        },
        # Add more course data as needed
    ]
    return render(request, 'home.html', {'courses': courses})

def api_login(request):
    if request.user.is_authenticated:
        #DEBBUG
        pass
        #return HttpResponse('You are already logged in')

    if request.method != 'POST':
        return render(request, 'registration/login.html')

    username = request.POST.get('username')
    password = request.POST.get('password')

    print(username, password)

    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect('profile')
    else:
        return HttpResponse('Invalid login', status=401)

def register(request):
    if request.user.is_authenticated:
    #DEBUG
        pass
        #return HttpResponse('You are already logged in')

    if request.method != 'POST':
        return render(request, 'registration/register.html')

    username = request.POST.get('username')
    email = request.POST.get('email')
    password = request.POST.get('password')
    confirm_password = request.POST.get('confirm_password')
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    #bio = request.POST.get('bio')

    if password != confirm_password:
        print(password, confirm_password)
        return HttpResponse('Passwords do not match', status=400)

    #return HttpResponse('User created successfully')

    # Create user account
    User.objects.create_user(username=username, email=email, password=password, first_name=first_name, last_name=last_name)
    Student.objects.create(user=User.objects.get(username=username), bio=f"I'm new here {datetime.now()}")
    login(request, authenticate(username=username, password=password))
    return redirect('profile')

def profile(request):
    if not request.user.is_authenticated:
        print(request.user)
        return redirect('login')



    user = {
        'username': 'johndoe',
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'test@gmail.com',
        'bio' : 'I am a student at the University of Warsaw',
        'image_url': "https://media.istockphoto.com/id/1300845620/vector/user-icon-flat-isolated-on-white-background-user-symbol-vector-illustration.jpg?s=612x612&w=0&k=20&c=yBeyba0hUkh14_jgv1OKqIH0CCSWU_4ckRkAoy2p73o",
    }
    return render(request, 'profile.html', {'user': user})

def api_logout(request):
    logout(request)
    if request.method == 'POST':
        return HttpResponse('User logged out successfully')
    redirect('login')

def join_course(request):
    if request.method != 'POST':
        return HttpResponse('Method not allowed', status=405)

    course_code = request.POST.get('course_code')
    if not request.user.is_authenticated:
        return HttpResponse('You need to be logged in to join a course', status=401)
    CourseStudent.objects.create(student=Student.objects.get(user=request.user), course=Course.objects.get(course_code=course_code), permission='viewer')
    return HttpResponse('Course joined successfully')

def leave_course(request):
    if request.method != 'POST':
        return HttpResponse('Method not allowed', status=405)

    course_code = request.POST.get('course_code')
    if not request.user.is_authenticated:
        return HttpResponse('You need to be logged in to leave a course', status=401)
    CourseStudent.objects.get(student=Student.objects.get(user=request.user), course=Course.objects.get(course_code=course_code)).delete()
    return HttpResponse('Course left successfully')

def create_course(request):
    if request.method != 'POST':
        return HttpResponse('Method not allowed', status=405)

    course_name = request.POST.get('course_name')
    course_description = request.POST.get('course_description')
    if not request.user.is_authenticated:
        return HttpResponse('You need to be logged in to create a course', status=401)
    t = Course.objects.create(course_name=course_name, course_description=course_description)
    CourseStudent.objects.create(student=Student.objects.get(user=request.user), course=t, permission='owner')
    return HttpResponse('Course created successfully')

def course(request, course_id):
    c = Course.objects.get(id=course_id)
    print(c.name)
    if not c:
        return HttpResponse('Course not found', status=404)

    if c.public:
        return render(request, 'course.html', {'course': c})
    else:
        if not request.user.is_authenticated:
            return HttpResponse('You need to be logged in to view this course', status=401)

        #TODO: Change permissions to be more secure
        if CourseStudent.objects.get(student=Student.objects.get(user=request.user), course=c).permission != 'owner':
            return HttpResponse('You do not have permission to view this course', status=403)
        return render(request, 'course.html', {'course': c})
