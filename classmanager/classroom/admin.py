from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Terms
from django.contrib.auth.admin import UserAdmin
from .models import User,Student,StudentMarks,Teacher,Grader,StudentsInClass,StudentGrades
# Register your models here.

admin.site.register(User, UserAdmin)
admin.site.register(Student)
admin.site.register(StudentMarks)
admin.site.register(StudentGrades)
admin.site.register(Teacher)
admin.site.register(Grader)
admin.site.register(StudentsInClass)

@admin.register(Terms)
class TermsAdmin(ImportExportModelAdmin):
    list_display = ('Registration_Number','Name','Quiz1','Quiz2', 'Mid_Term', 'Final_Term','Project','Total','Grade','RGrade')
