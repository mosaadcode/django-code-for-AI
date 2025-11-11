from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
# from fees.models import Fees
from django.db.models import Sum
from .forms import StudentProfile
from human_resources.models import Employee
from student_affairs.models import Student as StudentAff
from django.http import JsonResponse
import json

current_year = '26-25'
def loginuser(request):
    if request.method == 'GET':
        return render(request, 'student/home.html', {'form':AuthenticationForm})
    else:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            data = json.loads(request.body)
            na_id = data ['na_id']
            try:
                employee = Employee.objects.get(na_id=na_id)
                code = employee.code
            except Employee.DoesNotExist:
                # code = 0
                 try:
                     student = StudentAff.objects.get(student_id=na_id,study_year=current_year)
                     code = student.code
                 except StudentAff.DoesNotExist:
                     code = 0
            return JsonResponse({'code':code,})
        else:
            user = authenticate(request, code=request.POST['username'],password=request.POST['password'])
            if user is None:
                return render(request, 'student/home.html', {'form':AuthenticationForm, 'error':'برجاء التأكد من الكود وكلمة المرور'})
            else:
                login(request, user)
                if user.is_employ == False:
                    studentaff = StudentAff.objects.get(code=request.user.code)        
                    if studentaff.grade in ('الاول الابتدائى','الاول الاعدادى','الاول الثانوى'):
                        if studentaff.document_status == False:
                            logout(request)
                            return render(request, 'student/home.html', {'form':AuthenticationForm, 'error':'لا يمكن تسجيل المصروفات قبل إستيفاء كامل الأوراق المطلوبة, برجاء التواصل مع المدرسة'})
                        else:
                            if studentaff.application_status == False:
                                request.session['error'] ='برجاء تحديث البيانات التالية'
                                return redirect('application')
                            else:
                                return redirect('dashboard')
                    return redirect('dashboard')
                return redirect('home2')

# def home(request):
#     return render(request, 'student/home.html')

def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')

def profile(request):
        if request.method == 'GET':
            return render(request, 'student/profile.html', {'form':StudentProfile()})

        else:
            # add try: except to solve value Error
            try:
                # get the information from the post request and connect it with our form
                # form = StudentProfile(request.POST)
                # Create newtodo but dont't save it yet to the database
                # profile = form.save(commit=False)
                # set the user to newtodo
                # profile.student = request.user
                # newfee.grade = request.user.grade
                # newfee.school = request.user.school
                # save newtodo
                # newfee.save()
                # update student data
                request.user.father_mobile = request.POST['father_mobile']
                request.user.mother_mobile = request.POST['mother_mobile']
                request.user.phone_number = request.POST['phone_number']
                request.user.email = request.POST['email']
                request.user.save(update_fields=["father_mobile", "mother_mobile", "phone_number", "email"])
                # redirect user to currenttodos page
                # return redirect('dashboard')
                return render(request, 'student/profile.html', {'updated':'.تم حفظ البيانات بنجاح'})
            except ValueError:
                    # tell user when error hapen
                    return render(request, 'student/profile.html', {'form':StudentProfile(),'error':'برجاء مراجعة البيانات'})
