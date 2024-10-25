from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.models import User
import json

from StudentDashboard.models import Student, CourseStudent, Course, Attachment


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

def join_course(request, code):
    if not request.user.is_authenticated:
        return HttpResponse('You need to be logged in to join a course', status=401)
    try:
        course = Course.objects.get(code=code)
    except Course.DoesNotExist:
        return HttpResponse('Course not found', status=404)
    if CourseStudent.objects.filter(student=Student.objects.get(user=request.user), course=course):
        return HttpResponse('You are already enrolled in this course', status=400)

    CourseStudent.objects.create(student=Student.objects.get(user=request.user), course=course, permission=0)
    return redirect('course', course_id=course.id)


def leave_course(request, course_id):
    if not request.user.is_authenticated:
        return HttpResponse('You need to be logged in to leave a course', status=401)

    course = Course.objects.get(id=course_id)
    if not course:
        return HttpResponse('Course not found', status=404)

    try:
        courseStudent = CourseStudent.objects.get(student=Student.objects.get(user=request.user), course=course)
    except CourseStudent.DoesNotExist:
        return HttpResponse('You are not enrolled in this course', status=404)

    if courseStudent.permission == 2:
        course.delete()
    courseStudent.delete()
    return redirect('home')

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

    file = None

    if request.FILES:
        file = request.FILES['attachment']
        if (file.size / 1024) > 10000:
            return HttpResponse('File too large', status=400)

        #Only allow image files
        if not file.content_type in ['image/jpeg', 'image/png']:
            return HttpResponse('Invalid file type', status=400)


    if not request.user.is_authenticated:
        return HttpResponse('You need to be logged in to create a course', status=401)
    if file:
        t = Course.objects.create(name=course_name, description=course_description, public=is_public, image=file)
    else:
        t = Course.objects.create(name=course_name, description=course_description, public=is_public)
    t.set_code()
    print(t.code)
    CourseStudent.objects.create(student=Student.objects.get(user=request.user), course=t, permission=2)
    return redirect('course', course_id=t.id)

def course(request, course_id):
    c = Course.objects.get(id=course_id)
    print(c.name)
    if not c:
        return HttpResponse('Course not found', status=404)


    if request.method == "DELETE":
        if not request.user.is_authenticated:
            return HttpResponse('You need to be logged in to delete the attachment', status=401)
        if CourseStudent.objects.filter(student=Student.objects.get(user=request.user), course=c)[0].permission < 1:
            return HttpResponse('You do not have permission to delete this attachment', status=403)

        body = json.loads(request.body)

        attachment = Attachment.objects.filter(id = body["attachment_id"])
        if not attachment:
            return HttpResponse('Attachment not found', status=404)
        attachment.delete()
        return HttpResponse('Course deleted successfully', status=200)

    if request.method == 'POST' and request.FILES and 'file' in request.FILES:
        if not request.user.is_authenticated:
            return HttpResponse('You need to be logged in to upload an attachment', status=401)
        if CourseStudent.objects.filter(student=Student.objects.get(user=request.user), course=c)[0].permission < 1:
            return HttpResponse('You do not have permission to upload an attachment', status=403)


        print(request.FILES)
        file = request.FILES['file']
        if (file.size / 1024) > 10000:
            return HttpResponse('File too large', status=400)

        #Only allow pdf, image and text files
        if not file.content_type in ['application/pdf', 'image/jpeg', 'image/png', 'text/plain']:
            return HttpResponse('Invalid file type', status=400)

        name = file.name
        Attachment.objects.create(course=c, file=file, name=name)
        return HttpResponse('Attachment uploaded successfully', status=200)

    if request.method == 'POST':
        course_description = request.POST.get('course-description')
        name = request.POST.get('course-name')
        image = request.FILES.get('attachment')


        if not request.user.is_authenticated:
            return HttpResponse('You need to be logged in to update a course', status=401)
        if CourseStudent.objects.get(student=Student.objects.get(user=request.user), course=c).permission < 1:
            return HttpResponse('You do not have permission to update this course', status=403)

        if image:
            c.image = image
            c.save()
        if name:
            c.name = name
            c.save()
        if course_description:
            c.description = course_description
            c.save()
        return redirect('course', course_id=c.id)

    if c.public:
        if not CourseStudent.objects.filter(student=Student.objects.get(user=request.user), course=c):
            CourseStudent.objects.create(student=Student.objects.get(user=request.user), course=c, permission=0)
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

    attachments = Attachment.objects.filter(course=c)
    return render(request, 'course.html', {'course': c, 'attachments': attachments, "coursestudent": CourseStudent.objects.get(course=c, student=Student.objects.get(user=request.user))}, content_type='text/html; charset=utf-8')

def course_users(request, course_id):
    try:
        c = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return HttpResponse('Course not found', status=404)

    if not request.user.is_authenticated:
        return HttpResponse('You need to be logged in to view this page', status=401)

    if not CourseStudent.objects.filter(student=Student.objects.get(user=request.user), course=c):
        return HttpResponse('You do not have permission to view this page', status=403)

    users = CourseStudent.objects.filter(course=c)
    print(users)
    print(c.code)
    return render(request, 'course_users.html', {'course': c, 'users': users})

def edit_user(request, course_id, student_id):
    c = Course.objects.get(id=course_id)
    if not c:
        return HttpResponse('Course not found', status=404)

    if not request.user.is_authenticated:
        return HttpResponse('You need to be logged in to view this page', status=401)

    if CourseStudent.objects.filter(student=Student.objects.get(user=request.user), course=c)[0].permission < 2:
        return HttpResponse('You do not have permission to view this page', status=403)

    if request.method == 'POST':
        permission = request.POST.get('permission')
        print(permission)
        if permission == "-1":
            CourseStudent.objects.get(student=Student.objects.get(student_id=student_id), course=c).delete()
            return HttpResponse('User deleted successfully', status=200)
        courseStudent = CourseStudent.objects.get(student=Student.objects.get(student_id=student_id), course=c)
        courseStudent.permission = permission
        courseStudent.save()
        return HttpResponse('User updated successfully', status=200)

    student = CourseStudent.objects.get(student=Student.objects.get(student_id=student_id), course=c)
    return render(request, 'edit_user.html', {'course': c, 'user': student})

def delete_attachment(request, course_id, path):
    c = Course.objects.filter(id=course_id)
    if not c.exists():
        return HttpResponse('Course not found', status=404)

    c = c[0]

    if not request.user.is_authenticated:
        return HttpResponse('You need to be logged in to delete an attachment', status=401)

    if CourseStudent.objects.filter(student=Student.objects.get(user=request.user), course=c)[0].permission < 1:
        return HttpResponse('You do not have permission to delete an attachment', status=403)

    attachment = Attachment.objects.get(course=c, name=path)
    attachment.delete()
    return HttpResponse('Attachment deleted successfully', status=200)

def attachment(request, attachment_id):
    try:
        attachment = Attachment.objects.get(id=attachment_id)
    except Attachment.DoesNotExist:
        return HttpResponse('Attachment not found', status=404)
    print(attachment)

    # Get attachment file extension
    filename = attachment.file.name
    ext = filename.split('.')[-1]
    if ext == 'pdf':
        content_type = 'application/pdf'
    elif ext in ['jpg', 'jpeg']:
        content_type = 'image/jpeg'
    elif ext == 'png':
        content_type = 'image/png'
    else:
        content_type = 'text/plain'

    return HttpResponse(attachment.file, content_type=content_type)

