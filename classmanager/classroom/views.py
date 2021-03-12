from django.shortcuts import render,get_object_or_404,redirect
from django.views import generic
from django.views.generic import  (View,TemplateView,
                                  ListView,DetailView,
                                  CreateView,UpdateView,
                                  DeleteView)
from sqlalchemy import create_engine
import pandas as pd
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.
from classroom.forms import UserForm,ResultSheetForm,TeacherProfileForm,StudentProfileForm,GraderProfileForm,MarksForm,GradesForm,MessageForm,NoticeForm,AssignmentForm,SubmitForm,TeacherProfileUpdateForm,StudentProfileUpdateForm,GraderProfileUpdateForm
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout,update_session_auth_hash
from django.http import HttpResponseRedirect,HttpResponse
from classroom import models
from django.db.models import StdDev,Avg
import statistics
from classroom.models import StudentsInClass,ResultSheet,StudentMarks,ClassAssignment,SubmitAssignment,Student,Teacher,Grader,StudentGrades
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Q
from .resources import TermsResource
from tablib import Dataset
from .models import Terms


# For Teacher Sign Up
def TeacherSignUp(request):
    user_type = 'teacher'
    registered = False

    if request.method == "POST":
        user_form = UserForm(data = request.POST)
        teacher_profile_form = TeacherProfileForm(data = request.POST)

        if user_form.is_valid() and teacher_profile_form.is_valid():

            user = user_form.save()
            user.is_teacher = True
            user.save()

            profile = teacher_profile_form.save(commit=False)
            profile.user = user
            profile.save()

            registered = True
        else:
            print(user_form.errors,teacher_profile_form.errors)
    else:
        user_form = UserForm()
        teacher_profile_form = TeacherProfileForm()

    return render(request,'classroom/teacher_signup.html',{'user_form':user_form,'teacher_profile_form':teacher_profile_form,'registered':registered,'user_type':user_type})

########
# For Teacher Sign Up
def GraderSignUp(request):
    user_type = 'grader'
    registered = False

    if request.method == "POST":
        user_form = UserForm(data = request.POST)
        grader_profile_form = GraderProfileForm(data = request.POST)

        if user_form.is_valid() and grader_profile_form.is_valid():

            user = user_form.save()
            user.is_grader = True
            user.save()

            profile = grader_profile_form.save(commit=False)
            profile.user = user
            profile.save()

            registered = True
        else:
            print(user_form.errors,grader_profile_form.errors)
    else:
        user_form = UserForm()
        grader_profile_form = GraderProfileForm()

    return render(request,'classroom/grader_signup.html',{'user_form':user_form,'grader_profile_form':grader_profile_form,'registered':registered,'user_type':user_type})


########
###  For Student Sign Up
def StudentSignUp(request):
    user_type = 'student'
    registered = False

    if request.method == "POST":
        user_form = UserForm(data = request.POST)
        student_profile_form = StudentProfileForm(data = request.POST)

        if user_form.is_valid() and student_profile_form.is_valid():

            user = user_form.save()
            user.is_student = True
            user.save()

            profile = student_profile_form.save(commit=False)
            profile.user = user
            profile.save()

            registered = True
        else:
            print(user_form.errors,student_profile_form.errors)
    else:
        user_form = UserForm()
        student_profile_form = StudentProfileForm()

    return render(request,'classroom/student_signup.html',{'user_form':user_form,'student_profile_form':student_profile_form,'registered':registered,'user_type':user_type})

## Sign Up page which will ask whether you are teacher or student.
def SignUp(request):
    return render(request,'classroom/signup.html',{})

## login view.
def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username,password=password)

        if user:
            if user.is_active:
                login(request,user)
                return HttpResponseRedirect(reverse('home'))

            else:
                return HttpResponse("Account not active")

        else:
            messages.error(request, "Invalid Details")
            return redirect('classroom:login')
    else:
        return render(request,'classroom/login.html',{})

## logout view.
@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('home'))

## User Profile of student.
class StudentDetailView(LoginRequiredMixin,DetailView):
    context_object_name = "student"
    model = models.Student
    template_name = 'classroom/student_detail_page.html'

## User Profile for teacher.
class TeacherDetailView(LoginRequiredMixin,DetailView):
    context_object_name = "teacher"
    model = models.Teacher
    template_name = 'classroom/teacher_detail_page.html'
###
## User Profile for teacher.
class GraderDetailView(LoginRequiredMixin,DetailView):
    context_object_name = "grader"
    model = models.Grader
    template_name = 'classroom/grader_detail_page.html'

###

## Profile update for students.
@login_required
def StudentUpdateView(request,pk):
    profile_updated = False
    student = get_object_or_404(models.Student,pk=pk)
    if request.method == "POST":
        form = StudentProfileUpdateForm(request.POST,instance=student)
        if form.is_valid():
            profile = form.save(commit=False)
            if 'student_profile_pic' in request.FILES:
                profile.student_profile_pic = request.FILES['student_profile_pic']
            profile.save()
            profile_updated = True
    else:
        form = StudentProfileUpdateForm(request.POST or None,instance=student)
    return render(request,'classroom/student_update_page.html',{'profile_updated':profile_updated,'form':form})

## Profile update for teachers.
@login_required
def TeacherUpdateView(request,pk):
    profile_updated = False
    teacher = get_object_or_404(models.Teacher,pk=pk)
    if request.method == "POST":
        form = TeacherProfileUpdateForm(request.POST,instance=teacher)
        if form.is_valid():
            profile = form.save(commit=False)
            if 'teacher_profile_pic' in request.FILES:
                profile.teacher_profile_pic = request.FILES['teacher_profile_pic']
            profile.save()
            profile_updated = True
    else:
        form = TeacherProfileUpdateForm(request.POST or None,instance=teacher)
    return render(request,'classroom/teacher_update_page.html',{'profile_updated':profile_updated,'form':form})
#######
@login_required
def GraderUpdateView(request,pk):
    profile_updated = False
    grader = get_object_or_404(models.Grader,pk=pk)
    if request.method == "POST":
        form = GraderProfileUpdateForm(request.POST,instance=grader)
        if form.is_valid():
            profile = form.save(commit=False)
            if 'grader_profile_pic' in request.FILES:
                profile.grader_profile_pic = request.FILES['grader_profile_pic']
            profile.save()
            profile_updated = True
    else:
        form = GraderProfileUpdateForm(request.POST or None,instance=grader)
    return render(request,'classroom/grader_update_page.html',{'profile_updated':profile_updated,'form':form})
#######
## List of all students that teacher has added in their class.
def class_students_list(request):
    query = request.GET.get("q", None)
    students = StudentsInClass.objects.filter(teacher=request.user.Teacher)
    students_list = [x.student for x in students]
    qs = Student.objects.all()
    if query is not None:
        qs = qs.filter(
                Q(name__icontains=query)
                )
    qs_one = []
    for x in qs:
        if x in students_list:
            qs_one.append(x)
        else:
            pass
    context = {
        "class_students_list": qs_one,
    }
    template = "classroom/class_students_list.html"
    return render(request, template, context)

class ClassStudentsListView(LoginRequiredMixin,DetailView):
    model = models.Teacher
    template_name = "classroom/class_students_list.html"
    context_object_name = "teacher"

## For Marks obtained by the student in all subjects.
class StudentAllMarksList(LoginRequiredMixin,DetailView):
    model = models.Student
    template_name = "classroom/student_allmarks_list.html"
    context_object_name = "student"
def GradeClass(request):
    teacher = request.user.Teacher
    return render(request,'classroom/grade_a_class.html',{'teacher':teacher})
## To give marks to a student.
@login_required
def add_marks(request,pk):
    marks_given = False
    student = get_object_or_404(models.Student,pk=pk)
    if request.method == "POST":
        form = MarksForm(request.POST)
        if form.is_valid():
            marks = form.save(commit=False)
            marks.student = student
            marks.teacher = request.user.Teacher
            marks.save()
            messages.success(request,'Marks uploaded successfully!')
            return redirect('classroom:submit_list')
    else:
        form = MarksForm()
    return render(request,'classroom/add_marks.html',{'form':form,'student':student,'marks_given':marks_given})
###############

## To give grades to a student.
def add_grades(request,pk):
    marks_given = False
    student = get_object_or_404(models.Student,pk=pk)
    if request.method == "POST":
        form = GradesForm(request.POST)
        if form.is_valid():
            marks = form.save(commit=False)
            marks.student = student
            marks.teacher = request.user.Teacher
            marks.save()
            messages.success(request,'Marks uploaded successfully!')
            return redirect('classroom:grade_assignments')
    else:
        form = GradesForm()
    return render(request,'classroom/add_grades.html',{'form':form,'student':student,'marks_given':marks_given})


###############
## For updating marks.
@login_required
def update_marks(request,pk):
    marks_updated = False
    obj = get_object_or_404(StudentMarks,pk=pk)
    if request.method == "POST":
        form = MarksForm(request.POST,instance=obj)
        if form.is_valid():
            marks = form.save(commit=False)
            marks.save()
            marks_updated = True
    else:
        form = MarksForm(request.POST or None,instance=obj)
    return render(request,'classroom/update_marks.html',{'form':form,'marks_updated':marks_updated})

## For writing notice which will be sent to all class students.
@login_required
def add_notice(request):
    notice_sent = False
    teacher = request.user.Teacher
    students = StudentsInClass.objects.filter(teacher=teacher)
    students_list = [x.student for x in students]

    if request.method == "POST":
        notice = NoticeForm(request.POST)
        if notice.is_valid():
            object = notice.save(commit=False)
            object.teacher = teacher
            object.save()
            object.students.add(*students_list)
            notice_sent = True
    else:
        notice = NoticeForm()
    return render(request,'classroom/write_notice.html',{'notice':notice,'notice_sent':notice_sent})

## For student writing message to teacher.
@login_required
def write_message(request,pk):
    message_sent = False
    teacher = get_object_or_404(models.Teacher,pk=pk)

    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            mssg = form.save(commit=False)
            mssg.teacher = teacher
            mssg.student = request.user.Student
            mssg.save()
            message_sent = True
    else:
        form = MessageForm()
    return render(request,'classroom/write_message.html',{'form':form,'teacher':teacher,'message_sent':message_sent})

## For the list of all the messages teacher have received.
@login_required
def messages_list(request,pk):
    teacher = get_object_or_404(models.Teacher,pk=pk)
    return render(request,'classroom/messages_list.html',{'teacher':teacher})

## Student can see all notice given by their teacher.
@login_required
def class_notice(request,pk):
    student = get_object_or_404(models.Student,pk=pk)
    return render(request,'classroom/class_notice_list.html',{'student':student})

## To see the list of all the marks given by the techer to a specific student.
@login_required
def student_marks_list(request,pk):
    error = True
    student = get_object_or_404(models.Student,pk=pk)
    teacher = request.user.Teacher
    given_marks = StudentMarks.objects.filter(teacher=teacher,student=student)
    return render(request,'classroom/student_marks_list.html',{'student':student,'given_marks':given_marks})

## To add student in the class.
class add_student(LoginRequiredMixin,generic.RedirectView):

    def get_redirect_url(self,*args,**kwargs):
        return reverse('classroom:students_list')

    def get(self,request,*args,**kwargs):
        student = get_object_or_404(models.Student,pk=self.kwargs.get('pk'))

        try:
            StudentsInClass.objects.create(teacher=self.request.user.Teacher,student=student)
        except:
            messages.warning(self.request,'warning, Student already in class!')
        else:
            messages.success(self.request,'{} successfully added!'.format(student.name))

        return super().get(request,*args,**kwargs)

@login_required
def student_added(request):
    return render(request,'classroom/student_added.html',{})

## List of students which are not added by teacher in their class.
def students_list(request):
    query = request.GET.get("q", None)
    students = StudentsInClass.objects.filter(teacher=request.user.Teacher)
    students_list = [x.student for x in students]
    qs = Student.objects.all()
    if query is not None:
        qs = qs.filter(
                Q(name__icontains=query)
                )
    qs_one = []
    for x in qs:
        if x in students_list:
            pass
        else:
            qs_one.append(x)

    context = {
        "students_list": qs_one,
    }
    template = "classroom/students_list.html"
    return render(request, template, context)

## List of all the teacher present in the portal.
def teachers_list(request):
    query = request.GET.get("q", None)
    qs = Teacher.objects.all()
    if query is not None:
        qs = qs.filter(
                Q(name__icontains=query)
                )

    context = {
        "teachers_list": qs,
    }
    template = "classroom/teachers_list.html"
    return render(request, template, context)


####################################################

## Teacher uploading assignment.
@login_required
def upload_assignment(request):
    assignment_uploaded = False
    teacher = request.user.Teacher
    students = Student.objects.filter(user_student_name__teacher=request.user.Teacher)
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES)
        if form.is_valid():
            upload = form.save(commit=False)
            upload.teacher = teacher
            students = Student.objects.filter(user_student_name__teacher=request.user.Teacher)
            upload.save()
            upload.student.add(*students)
            assignment_uploaded = True
    else:
        form = AssignmentForm()
    return render(request,'classroom/upload_assignment.html',{'form':form,'assignment_uploaded':assignment_uploaded})

## Students getting the list of all the assignments uploaded by their teacher.
@login_required
def class_assignment(request):
    student = request.user.Student
    assignment = SubmitAssignment.objects.filter(student=student)
    assignment_list = [x.submitted_assignment for x in assignment]
    return render(request,'classroom/class_assignment.html',{'student':student,'assignment_list':assignment_list})

## List of all the assignments uploaded by the teacher himself.
@login_required
def assignment_list(request):
    teacher = request.user.Teacher
    return render(request,'classroom/assignment_list.html',{'teacher':teacher})

## For updating the assignments later.
@login_required
def update_assignment(request,id=None):
    obj = get_object_or_404(ClassAssignment, id=id)
    form = AssignmentForm(request.POST or None, instance=obj)
    context = {
        "form": form
    }
    if form.is_valid():
        obj = form.save(commit=False)
        if 'assignment' in request.FILES:
            obj.assignment = request.FILES['assignment']
        obj.save()
        messages.success(request, "Updated Assignment".format(obj.assignment_name))
        return redirect('classroom:assignment_list')
    template = "classroom/update_assignment.html"
    return render(request, template, context)

## For deleting the assignment.
@login_required
def assignment_delete(request, id=None):
    obj = get_object_or_404(ClassAssignment, id=id)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Assignment Removed")
        return redirect('classroom:assignment_list')
    context = {
        "object": obj,
    }
    template = "classroom/assignment_delete.html"
    return render(request, template, context)

## For students submitting their assignment.
@login_required
def submit_assignment(request, id=None):
    student = request.user.Student
    assignment = get_object_or_404(ClassAssignment, id=id)
    teacher = assignment.teacher
    if request.method == 'POST':
        form = SubmitForm(request.POST, request.FILES)
        if form.is_valid():
            upload = form.save(commit=False)
            upload.teacher = teacher
            upload.student = student
            upload.submitted_assignment = assignment
            upload.save()
            return redirect('classroom:class_assignment')
    else:
        form = SubmitForm()
    return render(request,'classroom/submit_assignment.html',{'form':form,})

## To see all the submissions done by the students.
@login_required
def submit_list(request):
    teacher = request.user.Teacher
    return render(request,'classroom/submit_list.html',{'teacher':teacher})
@login_required
def grade_assignments(request):
    teacher = request.user.Teacher
    return render(request,'classroom/grade_assignments.html',{'teacher':teacher})

##################################################################################################

## For changing password.
@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(data=request.POST , user=request.user)

        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, "Password changed")
            return redirect('home')
        else:
            return redirect('classroom:change_password')
    else:
        form = PasswordChangeForm(user=request.user)
        args = {'form':form}
        return render(request,'classroom/change_password.html',args)
def excel_delete():
    obj = Terms.objects.all()
    for i in obj:
        i.delete()
    return 0

def export(request):
    terms_resource = TermsResource()
    dataset = terms_resource.export()
    response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="terms.xls"'
    return response
def absolute(request,pk):
    error = True
    simple_upload(pk)
    if request.method=='POST':
        action = get_object_or_404(models.ResultSheet,pk=pk)
    result_attributes = Terms.objects.all()
    return render(request,'classroom/absolute.html',{'result_attributes':result_attributes})
def relative(request,pk):
    error = True
    simple_upload(pk)
    if request.method=='POST':
        action = get_object_or_404(models.ResultSheet,pk=pk)

    result_attributes = Terms.objects.all()
    array=[]
    for i in result_attributes:
        array.append(i.Total)
    sd = statistics.stdev(array)
    m = statistics.mean(array)
    for i in result_attributes:

        if i.Total > m + 1.5 * sd:
            i.RGrade = "A+"
        elif (i.Total > m + 1.0 * sd) and (i.Total <= m + 1.25 * sd):
            i.RGrade = "A"
        elif (i.Total > m + 1.0 * sd) and (i.Total <= m + 1.25 * sd):
            i.RGrade = "A-"
        elif (i.Total > m + 0.5 * sd) and (i.Total <= m + 1.0 * sd):
            i.RGrade = "B+"
        elif (i.Total > m ) and (i.Total <= m + 0.5 * sd) :
            i.RGrade = "B-"
        elif (i.Total > m -0.5 * sd) and (i.Total <= m):
            i.RGrade = "B"
        elif (i.Total > m - 1.0 * sd) and (i.Total <=m -0.5 * sd):
            i.RGrade = "C+"
        elif (i.Total > m - 1.25 * sd) and (i.Total <=m - 1.0 * sd):
            i.RGrade = "C-"
        elif (i.Total > m - 1.5 * sd) and (i.Total <= m - 1.25 * sd):
            i.RGrade = "C"
        else:
            i.RGrade = "F"
        
    return render(request,'classroom/relative.html',{'result_attributes':result_attributes})
def simple_upload(a):
    excel_delete()

    for i in ResultSheet.objects.all():
        if i.id==a:
            terms_resource = TermsResource()
            dataset = Dataset()
            new_terms = i.result_sheet

            imported_data = dataset.load(new_terms.read(),format='xlsx')
            #print(imported_data)
            
            for data in imported_data:

                value = Terms(
                    data[0],
                    data[1],
                    data[2],
                    data[3],
                    data[4],
                    data[5],
                    data[6],
                    data[7],

                        )
                value.save()       
                
        #result = person_resource.import_data(dataset, dry_run=True)  # Test the data import

        #if not result.has_errors():
        #    person_resource.import_data(dataset, dry_run=False)  # Actually import now

    return  0


@login_required
def upload_result_sheet(request):

    sheet_uploaded = False
    teacher = request.user.Teacher
    students = Student.objects.filter(user_student_name__teacher=request.user.Teacher)
    if request.method == 'POST':
        form = ResultSheetForm(request.POST, request.FILES)
        if form.is_valid():
            upload = form.save(commit=False)
            upload.teacher = teacher
            students = Student.objects.filter(user_student_name__teacher=request.user.Teacher)
            upload.save()
            upload.student.add(*students)
            sheet_uploaded = True
    else:
        form = ResultSheetForm()
    return render(request,'classroom/upload_result_sheet.html',{'form':form,'sheet_uploaded':sheet_uploaded})

## List of all the resultsuploaded by the teacher himself.
@login_required
def result_list(request):
    student = request.user.Student
    return render(request,'classroom/result_list.html',{'student':student})

def result_sheet_delete(request, id=None):
    obj = get_object_or_404(ResultSheet, id=id)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Result Sheet Removed")
        return redirect('classroom:grade_a_class')
    context = {
        "object": obj,
    }
    template = "classroom/result_sheet_delete.html"
    return render(request, template, context)
