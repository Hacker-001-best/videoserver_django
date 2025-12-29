from django.contrib.auth.models import AbstractUser
from django.db import models


class video(models.Model):
    video_name = models.CharField(max_length=255)
    teacher = models.ForeignKey( 'teacher', on_delete=models.PROTECT)
    lesson = models.ForeignKey('lessons', on_delete=models.PROTECT)
    lesson_category = models.ForeignKey( 'lesson_category' , on_delete=models.PROTECT)
    video_path = models.CharField(max_length=255)
    upload_date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.video_name


class teacher(AbstractUser):
    department = models.ForeignKey('department', on_delete=models.PROTECT, null=True, blank=True)
    faculty = models.ForeignKey('faculty', on_delete=models.PROTECT, null=True, blank=True)
    def __str__(self):
        return self.username



class department(models.Model):
    department_name = models.CharField(max_length=50,unique=True)
    faculty = models.ForeignKey('faculty', on_delete=models.PROTECT)
    def __str__(self):
        return self.department_name

class lessons(models.Model):
    lesson_name = models.CharField(max_length=50,unique=True)
    def __str__(self):
        return self.lesson_name

class lesson_category(models.Model):
    category_name = models.CharField(max_length=50,unique=True)
    def __str__(self):
        return self.category_name



class faculty(models.Model):
    faculty_name = models.CharField(max_length=50,unique=True)
    def __str__(self):
        return self.faculty_name










