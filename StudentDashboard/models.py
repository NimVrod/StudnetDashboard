from random import randint

from django.db import models

class Course(models.Model):
    course_name = models.CharField(max_length=50)
    course_code = models.CharField(max_length=10)
    course_description = models.CharField()
    owner = models.ForeignKey('auth.User', related_name='courses', on_delete=models.CASCADE)

    def __str__(self):
        return self.course_name

    def generate_course_code(self):
        self.course_code = f"{self.course_name[:3].upper()}-{randint(100, 999)}"
        # TODO: Check if course code already exists