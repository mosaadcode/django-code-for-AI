from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
# from fees.models import Fees
from django.db.models import Sum
# from .forms import StudentProfile
from human_resources.models import Employee
from student_affairs.models import Student as StudentAff
from fees.models import Fee
from fees.forms import FeesForm
from django.http import JsonResponse
import json

def fis_loginuser(request):
    if request.method == 'GET':
        return render(request, 'fis/home2.html', {'form':AuthenticationForm})
    else:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            data = json.loads(request.body)
            na_id = data ['na_id']
            try:
                employee = Employee.objects.get(na_id=na_id)
                code = employee.code
            except Employee.DoesNotExist:
                 code = 0

            return JsonResponse({'code':code,})
        else:
            user = authenticate(request, code=request.POST['username'],password=request.POST['password'])
            if user is None:
                return render(request, 'fis/home2.html', {'form':AuthenticationForm, 'error':'Check Student code and Password'})
            else:
                login(request, user)
                if not user.is_employ:
                    # studentaff = StudentAff.objects.get(code=request.user.code)
                    return redirect('fis_dashboard')
                return redirect('home2')
            
def fis_dashboard(request):
        if request.method == 'GET':  
            student=request.user
            if len(str(request.user.living_area)) > 4 :
                bus = True
            else :
                bus = False
            msg = request.session.get('msg')
            error = request.session.get('error')
            request.session['msg'] = ''
            request.session['error'] = ''
            context = {
                'bus':bus,
                'msg':msg,
                'error':error,
                'form':FeesForm(),
            }
            return render(request, 'fis/fis_dashboard.html',context)
        else:
            try:
                form = FeesForm(request.POST)
                newfee = form.save(commit=False)
                newfee.student = request.user
                newfee.school = request.user.school
     
                newfee.save()
                request.session['msg'] = 'Thank you, we will check the payment'
                return redirect('fis_dashboard')
            except ValueError:
                            # tell user when error hapen
                            return render(request, 'fis/fis_dashboard.html', {'form':FeesForm(),'error':'Check Payment Information.'})

def fis_logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('fis_home')
        
def payments(request):
    fees = Fee.objects.filter(student=request.user.id,year=request.user.year,kind__in = ('دراسية','سيارة','Books','Tours','USD')).exclude(school__in=('Out-b', 'Out-g')).order_by('payment_date')
    return render(request, 'fis/fis_payments.html',{'fees':fees})