from random import randint

from django.db import models

class Course(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=10)
    description = models.CharField(max_length=8000)
    public = models.BooleanField(default=False)

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

