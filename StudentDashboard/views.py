from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.models import User
import json

from StudentDashboard.models import Student, CourseStudent, Course, Attachment

from django.shortcuts import render

def error_404_view(request, exception):
    context = {
        'error_code': '404',
        'error_message': 'Nie znaleziono strony',
        'error_description': 'Strona, której szukasz, nie istnieje. Sprawdź, czy adres URL jest poprawny.',
    }
    return render(request, 'error.html', context, status=404)

def error_500_view(request):
    context = {
        'error_code': '500',
        'error_message': 'Wystąpił błąd serwera',
        'error_description': 'Spróbuj ponownie później.',
    }
    return render(request, 'error.html', context, status=500)

def error_view(request, error_code, error_message, error_description):
    context = {
        'error_code': error_code,
        'error_message': error_message,
        'error_description': error_description,
    }
    return render(request, 'error.html', context, status=error_code)

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
        pass
        return HttpResponse('You are already logged in')

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
        return redirect(error_view, 401, 'Nieautoryzwany', 'Zły login lub hasło')

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
        return redirect(error_view, 400, 'Bad Request', 'Hasła nie pasują do siebie')

    #return HttpResponse('User created successfully')

    # Check if username or email is already taken
    if User.objects.filter(username=username) or User.objects.filter(email=email):
        return redirect(error_view, 400, 'Zajęte', 'Nazwa użytkownika lub email jest już zajęty')

    # Create user account
    try:
        User.objects.create_user(username=username, email=email, password=password, first_name=first_name, last_name=last_name)
    except Exception as e:
        print(e)
        return redirect(error_view, 400, 'Bad Request', 'Nie udało się stworzyć użytkownika')
    Student.objects.create(user=User.objects.get(username=username), bio=f"Jestem tu nowy {datetime.now()}")
    login(request, authenticate(username=username, password=password))
    return redirect('profile')

def profile(request):
    if not request.user.is_authenticated:
        print(request.user)
        return redirect('login')


    if request.method == 'POST':
        if request.POST.get('current_password') and not request.user.check_password(request.POST.get('current_password')):
            return redirect(error_view, 400, 'Bad Request', 'Złe hasło')

        bio = request.POST.get('bio')
        student = Student.objects.get(user=request.user)
        student.bio = bio
        student.save()

        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_new_password')
        if new_password != confirm_password and new_password:
            return redirect(error_view, 400, 'Bad Request', 'Złe hasło')
        if new_password:
            request.user.set_password(new_password)
            request.user.save()

        username = request.POST.get('username')
        if username:
            request.user.username = username
            request.user.save()


        return redirect('profile')

    student = Student.objects.get(user=request.user)
    user = {
        'username': request.user.username,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'email': request.user.email,
        'bio' : student.bio,
    }
    return render(request, 'profile.html', {'user': user})

def api_logout(request):
    logout(request)
    if request.method == 'POST':
        return redirect(error_view, 200, 'OK', 'Wylogowano pomyślnie')
    redirect('login')

def join_course(request, code):
    if not request.user.is_authenticated:
        return redirect('login')
    try:
        course = Course.objects.get(code=code)
    except Course.DoesNotExist:
        return redirect(error_view, 404, 'Nie znaleziono', 'Kurs nie istnieje')
    if CourseStudent.objects.filter(student=Student.objects.get(user=request.user), course=course):
        return redirect(error_view, 400, 'Zajęte', 'Jesteś już zapisany na ten kurs')

    CourseStudent.objects.create(student=Student.objects.get(user=request.user), course=course, permission=0)
    return redirect('course', course_id=course.id)


def leave_course(request, course_id):
    if not request.user.is_authenticated:
        return redirect('login')

    course = Course.objects.get(id=course_id)
    if not course:
        return redirect(error_view, 404, 'Nie znaleziono', 'Kurs nie istnieje')

    try:
        courseStudent = CourseStudent.objects.get(student=Student.objects.get(user=request.user), course=course)
    except CourseStudent.DoesNotExist:
        return redirect(error_view, 404, 'Nie znaleziono', 'Nie jesteś zapisany na ten kurs')

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
            return redirect(error_view, 400, 'Za duży', 'Ten plik jest za duży')

        #Only allow image files
        if not file.content_type in ['image/jpeg', 'image/png']:
            return redirect(error_view, 400, 'Zły typ', 'Dozwolone formaty to jpeg i png')


    if not request.user.is_authenticated:
        return redirect('login')
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
        return redirect(error_view, 404, 'Nie znaleziono', 'Kurs nie istnieje')


    if request.method == "DELETE":
        if not request.user.is_authenticated:
            return redirect('login')
        if CourseStudent.objects.filter(student=Student.objects.get(user=request.user), course=c)[0].permission < 1:
            return redirect(error_view, 403, 'Brak uprawnień', 'Nie masz uprawnień do usunięcia kursu')

        body = json.loads(request.body)

        attachment = Attachment.objects.filter(id = body["attachment_id"])
        if not attachment:
            return HttpResponse('Attachment not found', status=404)
        attachment.delete()
        return HttpResponse('Attachment deleted successfully', status=200)

    if request.method == 'POST' and request.FILES and 'file' in request.FILES:
        if not request.user.is_authenticated:
            return redirect('login')
        if CourseStudent.objects.filter(student=Student.objects.get(user=request.user), course=c)[0].permission < 1:
            return redirect(error_view, 403, 'Brak uprawnień', 'Nie masz do tego uprawnień')


        print(request.FILES)
        file = request.FILES['file']
        if (file.size / 1024) > 10000:
            return redirect(error_view, 400, 'Za duży', 'Ten plik jest za duży')

        #Only allow pdf, image and text files
        if not file.content_type in ['application/pdf', 'image/jpeg', 'image/png', 'text/plain']:
            return redirect(error_view, 400, 'Zły typ', 'Dozwolone formaty to jpeg/png/pdf/txt')

        name = file.name
        Attachment.objects.create(course=c, file=file, name=name)
        return redirect('course', course_id=c.id)

    if request.method == 'POST':
        course_description = request.POST.get('course-description')
        name = request.POST.get('course-name')
        image = request.FILES.get('attachment')


        if not request.user.is_authenticated:
            return redirect('login')
        if CourseStudent.objects.get(student=Student.objects.get(user=request.user), course=c).permission < 1:
            return redirect(error_view, 403, 'Brak uprawnień', 'Nie masz do tego uprawnień')

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
            return redirect('login')

        # Check if user has permission to view course
        try:
            t = CourseStudent.objects.get(student=Student.objects.get(user=request.user), course=c)
        except CourseStudent.DoesNotExist:
            t = None
        print(t)
        if not t:
            return redirect(error_view, 403, 'Brak uprawnień', 'Nie masz do tego uprawnień')

    attachments = Attachment.objects.filter(course=c)
    return render(request, 'course.html', {'course': c, 'attachments': attachments, "coursestudent": CourseStudent.objects.get(course=c, student=Student.objects.get(user=request.user))}, content_type='text/html; charset=utf-8')

def course_users(request, course_id):
    try:
        c = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return redirect(error_view, 404, 'Nie znaleziono', 'Kurs nie istnieje')

    if not request.user.is_authenticated:
        return redirect('login')

    if not CourseStudent.objects.filter(student=Student.objects.get(user=request.user), course=c):
        return redirect(error_view, 403, 'Brak uprawnień', 'Nie masz do tego uprawnień')

    users = CourseStudent.objects.filter(course=c)
    print(users)
    print(c.code)
    return render(request, 'course_users.html', {'course': c, 'users': users})

def edit_user(request, course_id, student_id):
    c = Course.objects.get(id=course_id)
    if not c:
        return redirect(error_view, 404, 'Nie znaleziono', 'Kurs nie istnieje')

    if not request.user.is_authenticated:
        return redirect('login')

    if CourseStudent.objects.filter(student=Student.objects.get(user=request.user), course=c)[0].permission < 2:
        return redirect(error_view, 403, 'Brak uprawnień', 'Nie masz do tego uprawnień')

    if request.method == 'POST':
        permission = request.POST.get('permission')
        print(permission)
        if permission == "-1":
            CourseStudent.objects.get(student=Student.objects.get(student_id=student_id), course=c).delete()
            return redirect(error_view, 200, 'OK', 'Użytkownik usunięty pomyślnie')
        courseStudent = CourseStudent.objects.get(student=Student.objects.get(student_id=student_id), course=c)
        courseStudent.permission = permission
        courseStudent.save()
        return redirect('course_users', course_id=course_id)

    student = CourseStudent.objects.get(student=Student.objects.get(student_id=student_id), course=c)
    return render(request, 'edit_user.html', {'course': c, 'user': student})

def delete_attachment(request, course_id, path):
    c = Course.objects.filter(id=course_id)
    if not c.exists():
        return redirect(error_view, 404, 'Nie znaleziono', 'Kurs nie istnieje')

    c = c[0]

    if not request.user.is_authenticated:
        return redirect('login')

    if CourseStudent.objects.filter(student=Student.objects.get(user=request.user), course=c)[0].permission < 1:
        return redirect(error_view, 403, 'Brak uprawnień', 'Nie masz do tego uprawnień')

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

