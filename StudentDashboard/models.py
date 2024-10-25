from random import randint

from django.db import models

class Course(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=10)
    description = models.CharField(max_length=8000)
    public = models.BooleanField(default=False)
    image = models.ImageField(upload_to='course_images/', default='/course_images/default.jpg')

    def __str__(self):
        return self.name

    def set_code(self):
        self.code = self.name[:3].upper() + str(randint(1000, 9999))
        self.save()

class Attachment(models.Model):
    id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    file = models.FileField(upload_to='attachments/')
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Student(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    student_id = models.AutoField(primary_key=True)
    bio = models.CharField(max_length=1000)

    def __str__(self):
        return self.user.username


class CourseStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    permission = models.IntegerField(choices=[(2, 'owner'), (1, 'editor'), (0, 'viewer')])

    def __str__(self):
        return self.student.user.username + ' - ' + self.course.name

    def get_permission_string(self):
        return dict(self._meta.get_field('permission').choices)[self.permission]