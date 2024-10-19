from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.models import User

from StudentDashboard.models import Student, CourseStudent, Course


def home(request):

    courses = Course.objects.filter(public=True)
    courses = list(courses)
    if request.user.is_authenticated:
        permissions = CourseStudent.objects.filter(student=Student.objects.get(user=request.user))
        for permission in permissions:
            if permission.permission >= 0:
                courses.append(Course.objects.get(id=permission.course.id))
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


    student = Student.objects.get(user=request.user)
    user = {
        'username': request.user.username,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'email': request.user.email,
        'bio' : student.bio,
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
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method != 'POST':
        return render(request, 'course_create.html')

    course_name = request.POST.get('course-name')
    course_description = request.POST.get('course-description')
    is_public = request.POST.get('is-public')

    if is_public == 'on':
        is_public = True
    else:
        is_public = False

    if not request.user.is_authenticated:
        return HttpResponse('You need to be logged in to create a course', status=401)
    t = Course.objects.create(name=course_name, description=course_description, public=is_public)
    CourseStudent.objects.create(student=Student.objects.get(user=request.user), course=t, permission=2)
    return redirect('course', course_id=t.id)

def course(request, course_id):
    c = Course.objects.get(id=course_id)
    print(c.name)
    if not c:
        return HttpResponse('Course not found', status=404)

    if request.method == 'POST':
        course_description = request.POST.get('course_description')

        print(request.user.is_authenticated)
        if not request.user.is_authenticated:
            return HttpResponse('You need to be logged in to update a course', status=401)
        if CourseStudent.objects.get(student=Student.objects.get(user=request.user), course=c).permission < 1:
            return HttpResponse('You do not have permission to update this course', status=403)

        print(course_id)
        # Course.objects.get(course_id=course_id).update(course_description=course_description)
        return HttpResponse('Course updated successfully', status=200)

    if c.public:
        if not CourseStudent.objects.filter(student=Student.objects.get(user=request.user), course=c):
            CourseStudent.objects.create(student=Student.objects.get(user=request.user), course=c, permission=0)
        return render(request, 'course.html', {'course': c})
    else:
        if not request.user.is_authenticated:
            return HttpResponse('You need to be logged in to view this course', status=401)

        # Check if user has permission to view course
        try:
            t = CourseStudent.objects.get(student=Student.objects.get(user=request.user), course=c)
        except CourseStudent.DoesNotExist:
            t = None
        print(t)
        if not t:
            return HttpResponse('You do not have permission to view this course', status=403)
        return render(request, 'course.html', {'course': c})
