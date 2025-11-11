from django.shortcuts import render,redirect,get_object_or_404
from .models import Employee,SalaryItem,MonthN as Month,Permission,Vacation,Employee_month,Time_setting
from .forms import PermForm,VacationForm,EmployeeContact
from datetime import datetime,date,timedelta
from django.http import JsonResponse
import json
from django.utils import timezone

try:
    published_month = Month.objects.get(published=True)
    pub_month = published_month.code[5:]
    pub_year = published_month.code[:4]
except Month.DoesNotExist:
    published_month = None
try:
    active_month = Month.objects.get(active=True)
    if int(active_month.code[5:])==1:
        month_start = date(int(active_month.code[:4])-1,12,16)
    else:
        month_start = date(int(active_month.code[:4]),int(active_month.code[5:])-1,16)
    month_end = date(int(active_month.code[:4]),int(active_month.code[5:]),15)
except Month.DoesNotExist:
    active_month = None

def home(request):
    msg = request.session.get('msg')
    request.session['msg'] = ''
    error = request.session.get('error')
    request.session['error'] = ''
    emp = Employee.objects.get(code=request.user.code)
    context = {
       'emp':emp,
       'msg':msg,
       'error':error,
       'base_template' : 'fis/base2.html' if request.user.school == 'FIS' else 'student/base.html'
    }
    if emp.school!='FIS' and not emp.rules_agreed:
        return redirect('rules')
    return render(request, 'human_resources/home.html',context)

def salary(request):
    if published_month != None:
        context = {
        'month':pub_month,
        'year':pub_year,
        'items':SalaryItem.objects.filter(employee__code=request.user.code,month=published_month).order_by('-value'),
        'base_template' : 'fis/base2.html' if request.user.school == 'FIS' else 'student/base.html'
        }
    else:
        context = {
        'base_template' : 'fis/base2.html' if request.user.school == 'FIS' else 'student/base.html'
        }
    return render(request, 'human_resources/salary.html',context)

# to auto get permission work time 
def get_work_time(type, work_time):
    if type == 'صباحي':
        return work_time.time_in, work_time.time_in_perm
    elif type == 'مسائي':
        return work_time.time_out_perm, work_time.time_out
# to fix dvided by zero when get percentage
def calculate_permission_percentage(used, total):
    if total > 0:
        return (used / total) * 100
    else:
        return 0
def calculate_vacation_percentage(used, total):
    if total > 0:
        return (used / total) * 100
    else:
        return 0


def perm(request):
    employee = Employee.objects.select_related('permission_setting','vacation_setting').get(code=request.user.code)
    try:
        employee_month = Employee_month.objects.get(employee=employee,month=active_month)
    except Employee_month.DoesNotExist:
        request.session['error'] = 'لم يتم العثور على السجل الشهري برجاء التواصل مع قسم شؤون العاملين'
        return redirect('home2')
    
    month_perms= Permission.objects.filter(employee=employee,month=active_month).order_by('-created')
    settings = employee.permission_setting
    times = employee.vacation_setting

    if settings is None or times is None:
        request.session['error'] = 'إعدادات اَذون غير صحيحة برجاء التواصل مع قسم شؤون العاملين'
        return redirect('home2')   
        
    total = settings.perms
    used = month_perms.count()
    unused = total - used
    used_perms_percentage = calculate_permission_percentage(used, total)
    unused_perms_percentage = 100 - used_perms_percentage
    over = employee_month.permissions - total

    # Check if there are any month_perms with ok2=False
    OpenPerm = month_perms.filter(ok2=False).exists()

    if request.method == 'GET':
        msg = request.session.get('msg')
        request.session['msg'] = ''
        error = request.session.get('error')
        request.session['error'] = ''
        if settings.is_perms == False:
            request.session['error'] = 'ليس لك الحق في إستخدام الاَذون'
            return redirect('home2')
        else:

            context = {
                'form':PermForm(),
                'msg':msg,
                'error':error,
                'settings':settings,
                'month':active_month,
                'month_start':month_start,
                'month_end':month_end,
                'month_perms':month_perms,
                'total':total,
                'used':used,
                'unused':unused,
                'used_perms_percentage' : used_perms_percentage,
                'unused_perms_percentage' :unused_perms_percentage,
                'over':over,  
                'OpenPerm' :OpenPerm,
                'base_template' : 'fis/base2.html' if request.user.school == 'FIS' else 'student/base.html'
            }
            return render( request, "human_resources/perm.html", context)

    else:       
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            data = json.loads(request.body)
            type = data ['type']
            date = data['date']
            work_time = Time_setting.objects.get(month=active_month, date=date, name=times)
            start_time, end_time = get_work_time(type, work_time)
            return JsonResponse({'start_time': start_time, 'end_time': end_time})
        else:
            if active_month is not None:
                unused_perms = request.POST.get('unused_perms')
                if used < total :
                    form = PermForm(request.POST)
                    if form.is_valid():
                        permission = form.save(commit=False)
                        permission.employee = employee
                        permission.school = employee.school
                        permission.month=active_month
                        permission.count=employee_month.permissions+1
                        permission.total=settings.perms
                        permission.save()
                        request.session['msg'] = '( تم تسجيل الإذن ( قيد الموافقة'
                        return redirect('perm')
                    else:
                        request.session['error'] = 'حدث خطأ , رجاء إعادة المحاولة'
                        return redirect('perm')
                else:
                    if settings.is_over == False:
                        request.session['error'] = 'تم استخدام جميع اَذون هذا الشهر وغير مسموح بالتجاوز'
                        return redirect('perm')
                    else:
                        form = PermForm(request.POST)
                        permission = form.save(commit=False)
                        permission.employee = employee
                        permission.school = employee.school
                        permission.month=active_month
                        permission.count=employee_month.permissions+1
                        permission.total=settings.perms
                        permission.save()
                        request.session['msg'] = ' ( تم تسجيل الإذن زائد ( سيتم الخصم من الراتب'
                        return redirect('perm')
            else:
                request.session['error'] = 'لا توجد شهور مفعلة'
                return redirect('perm')


def delete_permission(request, permission_id):
    try:
        permission = get_object_or_404(Permission, id=permission_id)    
        # Check if both ok1 and ok2 are False
        if  not permission.ok2:
            permission.delete()
    except:
        pass
    
    return redirect('perm')




def vacation(request):
    employee = Employee.objects.select_related('vacation_setting').get(code=request.user.code)
    try:
        employee_month = Employee_month.objects.get(employee=employee,month=active_month)
    except Employee_month.DoesNotExist:
        request.session['error'] = 'لم يتم العثور على السجل الشهري برجاء التواصل مع قسم شؤون العاملين'
        return redirect('home2')
    
    vacations= Vacation.objects.filter(employee=employee,month=active_month).order_by('-created')
    settings = employee.vacation_setting
    if settings is None:
        request.session['error'] = 'إعدادات إجازات غير صحيحة برجاء التواصل مع قسم شؤون العاملين'
        return redirect('home2')  
         
    dayoff_settings = Time_setting.objects.filter(month=active_month,name=settings,dayoff=True)
    total_vacations = settings.vacations
    used_vacations = employee.used_vacations
    unused_vacations = total_vacations - used_vacations
    used_vacations_percentage = calculate_vacation_percentage(used_vacations, total_vacations)
    unused_vacations_percentage = 100 - used_vacations_percentage
    total_vacations_s = settings.vacations_s
    used_vacations_s = employee.used_vacations_s
    unused_vacations_s = total_vacations_s - used_vacations_s
    used_vacations_s_percentage = calculate_vacation_percentage(used_vacations_s, total_vacations_s)
    unused_vacations_s_percentage = 100 - used_vacations_s_percentage
    total_absents = settings.absents
    used_absents = vacations.filter(month=active_month,type='إذن غياب').count()
    unused_absents = total_absents - used_absents
    used_absents_percentage = calculate_permission_percentage(used_absents, total_absents)
    unused_absents_percentage = 100 - used_absents_percentage

    is_absent = True if settings.is_absent and used_absents < total_absents else False
    is_vacation = True if settings.is_vacation and used_vacations < total_vacations else False
    is_vacation_s = True if settings.is_vacation_s and used_vacations_s < total_vacations_s else False

    max_vacation = min(unused_vacations-1,15)
    max_vacation_s = min(unused_vacations_s-1,15)


    # Check if there are any vacation with ok2=False
    OpenVacation = vacations.filter(ok2=False).exists()

    if request.method == 'GET':
        msg = request.session.get('msg')
        request.session['msg'] = ''
        error = request.session.get('error')
        request.session['error'] = ''
        if settings.is_vacation == False and settings.is_vacation_s == False and settings.is_absent == False:
            request.session['error'] = 'ليس لك الحق في إستخدام الإجازات'
            return redirect('home2')
        else:
            context = {
                'form':VacationForm(),
                'msg':msg,
                'error':error,
                'month_start':month_start,
                'month_end':month_end,
                'settings':settings,
                'vacations':vacations,
                'total_vacations':total_vacations,
                'total_vacations_s':total_vacations_s,
                'total_absents':total_absents,
                'used_vacations':used_vacations,
                'used_vacations_s':used_vacations_s,
                'used_absents':used_absents,
                'unused_vacations':unused_vacations,
                'unused_vacations_s':unused_vacations_s,
                'unused_absents':unused_absents,
                'used_vacations_percentage' : used_vacations_percentage,
                'unused_vacations_percentage' :unused_vacations_percentage,
                'used_vacations_s_percentage' : used_vacations_s_percentage,
                'unused_vacations_s_percentage' :unused_vacations_s_percentage,
                'used_absents_percentage':used_absents_percentage,
                'unused_absents_percentage':unused_absents_percentage,
                'OpenVacation' :OpenVacation,
                'is_absent':is_absent,
                'is_vacation':is_vacation,
                'is_vacation_s':is_vacation_s,
                'max_vacation':max_vacation,
                'max_vacation_s':max_vacation_s,
                'base_template' : 'fis/base2.html' if request.user.school == 'FIS' else 'student/base.html'
            }
            return render( request, "human_resources/vacation.html", context)


    else:
        
        form = VacationForm(request.POST, request.FILES)
        if form.is_valid():
            date_from = request.POST['date_from']
            date_to = request.POST['date_to']

            # Parse date strings into datetime objects
            date_from = datetime.strptime(date_from, '%Y-%m-%d')
            date_to = datetime.strptime(date_to, '%Y-%m-%d')
            # Create a list of day-offs based on the dayoff_settings
            dayoffs = [setting.date for setting in dayoff_settings]

            days_count = 0
            days = []  # Initialize an empty list to store the day component of non-day-off dates

            # Iterate through the date range
            current_date = date_from
            while current_date <= date_to:
                # Check if the current date is not a day-off
                if current_date.date() not in dayoffs:
                    days_count += 1
                    days.append(current_date.date().day)  # Add the day component to the 'days' list
                current_date += timedelta(days=1)

            vacation = form.save(commit=False)
            vacation.employee = Employee.objects.get(code=request.user.code)
            vacation.school = request.user.school
            vacation.month = active_month
            vacation.count = days_count
            vacation.days = days
            if request.POST['type'] == 'مرضي':
                vacation.total = unused_vacations_s
            elif request.POST['type'] == 'من الرصيد':
                vacation.total = unused_vacations
            else:
                vacation.total = unused_absents
            vacation.save()

            request.session['msg'] = '( تم تسجيل الإجازة ( قيد الموافقة'
        else:
            request.session['error'] = form['photo'].errors
            # request.session['error'] = ' وحجم مناسب (jpg, jpeg, png, gif)يرجى التحقق من الصورة. يجب ان تكون احد الامتدادات التالية'

        return redirect('vacation')

def delete_vacation(request, vacation_id):
    try:
        vacation = get_object_or_404(Vacation, id=vacation_id)    
        # Check if both ok1 and ok2 are False
        if  not vacation.ok2:
            vacation.delete()
    except:
        pass
    
    return redirect('vacation')

def employee_contact(request):
        if request.method == 'GET':
            msg = request.session.get('msg')
            request.session['msg'] = ''
            error = request.session.get('error')
            request.session['error'] = ''

            employee = Employee.objects.get(code=request.user.code)
            context = {
                'msg':msg,
                'error':error,
                'form':EmployeeContact(instance=employee),
                'base_template' : 'fis/base2.html' if request.user.school == 'FIS' else 'student/base.html'
                }
            return render(request, 'human_resources/employee_contact.html',context)
        else:
            try:
                employee = Employee.objects.get(code=request.user.code)
                try:
                    employee.mobile_number = request.POST['mobile_number']
                    employee.phone_number = request.POST['phone_number']
                    employee.emergency_phone = request.POST['emergency_phone']
                    employee.email = request.POST['email']
                    employee.save()


                    request.session['msg'] = 'تم تعديل البيانات بنجاح'
                    return redirect('employee_contact')
                except Employee.DoesNotExist:
                    request.session['error'] = 'برجاء إدخال البيانات بشكل صحيح'
                    return redirect('employee_contact')
            except ValueError:
                    request.session['error'] = 'لا يمكن تعديل البيانات الاّن'
                    return redirect('employee_contact')
            
def rules(request):
    msg = request.session.get('msg', '')
    error = request.session.get('error', '')
    
    # Clear the messages from session after reading
    if 'msg' in request.session:
        del request.session['msg']
    if 'error' in request.session:
        del request.session['error']
    
    try:
        emp = Employee.objects.get(code=request.user.code)
    except Employee.DoesNotExist:
        # Handle case where employee doesn't exist
        emp = None
        error = 'لم يتم العثور على بيانات الموظف.'
    
    context = {
       'emp': emp,
       'msg': msg,
       'error': error,
       'base_template': 'fis/base2.html' if request.user.school == 'FIS' else 'student/base.html'
    }
    return render(request, 'human_resources/rules.html', context)

def agree_to_rules(request):
    if request.method == 'POST':
        try:
            emp = Employee.objects.get(code=request.user.code)
            if 'agree' in request.POST:
                emp.rules_agreed = True
                emp.rules_agreed_date = timezone.now()
                emp.save()
                request.session['msg'] = 'شكراً لك، لقد وافقت على اللائحة الداخلية بنجاح.'
            else:
                request.session['error'] = 'يجب الموافقة على الشروط والأحكام أولاً.'
        except Employee.DoesNotExist:
            request.session['error'] = 'لم يتم العثور على بيانات الموظف.'
        
        return redirect('rules')