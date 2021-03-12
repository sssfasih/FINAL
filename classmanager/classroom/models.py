from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.conf import settings
from django.db.models import StdDev,Avg
import statistics
# Create your models here.'Registration Number','Name', 'Mid Term', 'Final Term','Project','Attendance'
class Terms(models.Model):
    Registration_Number = models.CharField(max_length=30)
    Name=models.CharField(max_length=100, blank=True)
    Quiz1= models.IntegerField()
    Quiz2= models.IntegerField()
    Mid_Term=models.IntegerField()
    Final_Term= models.IntegerField()
    Project= models.IntegerField()
    Total = models.IntegerField(default=0)
    Grade = models.CharField(default='NONE', max_length=2)
    RGrade = models.CharField(default='NONE', max_length=2)
    def save(self, *args, **kwargs):
        self.Total = int(self.Quiz1) + int(self.Quiz2) + int(self.Mid_Term) + int(self.Final_Term) + int(self.Project)
        super(Terms, self).save(*args, **kwargs)
        if(self.Total>100):
            self.Grade = None
        if(self.Total>=90):
            self.Grade = 'A+'
        elif(self.Total>=80):
            self.Grade = 'A'
        elif(self.Total>=70):
            self.Grade = 'A-'
        elif(self.Total>=60):
            self.Grade = 'B+'
        elif(self.Total>=55):
            self.Grade = 'B'
        elif(self.Total>=50):
            self.Grade = 'B-'
        elif(self.Total>=45):
            self.Grade = 'C+'
        elif(self.Total>=40):
            self.Grade = 'C'
        elif(self.Total>=35):
            self.Grade = 'C-'
        elif(self.Total>=30):
            self.Grade = 'D'
        elif(self.Total<30):
            self.Grade = 'F' 
#......................................................

        super(Terms, self).save(*args, **kwargs)
class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    is_grader= models.BooleanField(default=False)

class Student(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,primary_key=True,related_name='Student')
    name=models.CharField(max_length=250)
    roll_no = models.CharField(max_length=50)
    email = models.EmailField(max_length=254)
    phone = models.IntegerField()
    student_profile_pic = models.ImageField(upload_to="classroom/student_profile_pic",blank=True)

    def get_absolute_url(self):
        return reverse('classroom:student_detail',kwargs={'pk':self.pk})

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['roll_no']

class Teacher(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,primary_key=True,related_name='Teacher')
    name = models.CharField(max_length=250)
    subject_name = models.CharField(max_length=250)
    email = models.EmailField(max_length=254)
    phone = models.IntegerField()
    teacher_profile_pic = models.ImageField(upload_to="classroom/teacher_profile_pic",blank=True)
    class_students = models.ManyToManyField(Student,through="StudentsInClass")

    def get_absolute_url(self):
        return reverse('classroom:teacher_detail',kwargs={'pk':self.pk})

    def __str__(self):
        return self.name
'''class Terms(models.Model):
    name = models.CharField(max_length=250)
    mid=models.IntegerField()
    final=models.IntegerField()
    project=models.IntegerField()
    attendance=models.IntegerField()
    grade=models.CharField(max_length=250)'''

class Grader(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,primary_key=True,related_name='grader')
    name = models.CharField(max_length=250)
    subject_name = models.CharField(max_length=250)
    email = models.EmailField(max_length=254)
    phone = models.IntegerField()
    grader_profile_pic = models.ImageField(upload_to="classroom/grader_profile_pic",blank=True)


    def get_absolute_url(self):
        return reverse('classroom:grader_detail',kwargs={'pk':self.pk})

    def __str__(self):
        return self.name



################

################

class StudentsInClass(models.Model):
    teacher = models.ForeignKey(Teacher,related_name="class_teacher",on_delete=models.CASCADE)
    student = models.ForeignKey(Student,related_name="user_student_name",on_delete=models.CASCADE)

    def __str__(self):
        return self.student.name

    class Meta:
        unique_together = ('teacher','student')

class MessageToTeacher(models.Model):
    student = models.ForeignKey(Student,related_name='student',on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher,related_name='messages',on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    message = models.TextField()
    message_html = models.TextField(editable=False)

    def __str__(self):
        return self.message

    def save(self,*args,**kwargs):
        self.message_html = misaka.html(self.message)
        super().save(*args,**kwargs)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['student','message']

class ClassNotice(models.Model):
    teacher = models.ForeignKey(Teacher,related_name='teacher',on_delete=models.CASCADE)
    students = models.ManyToManyField(Student,related_name='class_notice')
    created_at = models.DateTimeField(auto_now=True)
    message = models.TextField()
    message_html = models.TextField(editable=False)

    def __str__(self):
        return self.message

    def save(self,*args,**kwargs):
        self.message_html = misaka.html(self.message)
        super().save(*args,**kwargs)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['teacher','message']

class ClassAssignment(models.Model):
    student = models.ManyToManyField(Student,related_name='student_assignment')
    teacher = models.ForeignKey(Teacher,related_name='teacher_assignment',on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    assignment_name = models.CharField(max_length=250)
    assignment = models.FileField(upload_to='assignments')

    def __str__(self):
        return self.assignment_name

    class Meta:
        ordering = ['-created_at']

class SubmitAssignment(models.Model):
    student = models.ForeignKey(Student,related_name='student_submit',on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher,related_name='teacher_submit',on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    submitted_assignment = models.ForeignKey(ClassAssignment,related_name='submission_for_assignment',on_delete=models.CASCADE)
    submit = models.FileField(upload_to='Submission')

    def __str__(self):
        return "Submitted"+str(self.submitted_assignment.assignment_name)

    class Meta:
        ordering = ['-created_at']
class StudentMarks(models.Model):
    teacher = models.ForeignKey(Teacher,related_name='given_marks',on_delete=models.CASCADE)
    student = models.ForeignKey(Student,related_name="marks",on_delete=models.CASCADE)
    subject_name = models.CharField(max_length=250)
    marks_obtained = models.IntegerField()
    maximum_marks = models.IntegerField()
    grades_obtained = models.CharField(max_length=1)
    def __str__(self):
        return self.subject_name
    class Meta:
        ordering = ['-marks_obtained']
class StudentGrades(models.Model):
    teacher = models.ForeignKey(Teacher,related_name='given_grades',on_delete=models.CASCADE)
    student = models.ForeignKey(Student,related_name="grades",on_delete=models.CASCADE)
    subject_name = models.CharField(max_length=250)
    grades_obtained = models.IntegerField()

    def __str__(self):
        return self.subject_name
    class Meta:
        ordering = ['-grades_obtained']

class ResultSheet(models.Model):
    student = models.ManyToManyField(Student,related_name='student_result')
    teacher = models.ForeignKey(Teacher,related_name='teacher_upload',on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    sheet_name = models.CharField(max_length=250)
    result_sheet = models.FileField(upload_to='result_sheets')

    def __str__(self):
        return self.sheet_name

    class Meta:
        ordering = ['-created_at']