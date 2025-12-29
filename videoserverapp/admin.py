from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import *

# Register your models here.
admin.site.register(lessons)
admin.site.register(lesson_category)
admin.site.register(faculty)
class DepartmenAdmin(admin.ModelAdmin):
    list_display = ('department_name','faculty')
admin.site.register(department, DepartmenAdmin)

@admin.register(teacher)
class TeacherAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {'fields': ('department','faculty')}),
    )

class VideoAdmin(admin.ModelAdmin):
    list_display = ('video_name','teacher','lesson','lesson_category','video_path','upload_date')
admin.site.register(video,VideoAdmin)
