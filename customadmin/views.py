from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.models import User
from app.models import *
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib import messages, auth
# pylint: disable=unused-import
from customadmin.models import *
from notifications_app.tasks import broadcast_notification

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = auth.authenticate(username=username, password=password)

        if user is not None and user.is_superuser:
            auth.login(request, user)
            messages.success(request, 'Admin login successful')
            return redirect('/admin/insights/')  # Use a named URL pattern
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'login.html')

@login_required(login_url='admin_login')
def dashboard(request):
    # Query Employee instances
    employees = Employee.objects.all()

    # Use prefetch_related to retrieve related LoginHistory records for each Employee
    employees_with_loginhistory = employees.prefetch_related('loginhistory_set')

    # Pagination for employees
    page = Paginator(employees_with_loginhistory, 5)
    page_number = request.GET.get('page')
    page = page.get_page(page_number)

    userlevels = UserLevel.objects.filter(user__in=employees)

    unread_notifications = AdminNotification.objects.filter(user=request.user, is_read=False)

    # Calculate the count of unread notifications
    unread_count = unread_notifications.count()

    admin_notifications = AdminNotification.objects.filter(user=request.user)
    # print(notifications)



    context = {
        'page': page,
        'users': employees_with_loginhistory,  # Pass the updated queryset to the template
        'userlevels': userlevels,
        'admin_notifications': admin_notifications,
        'unread_count': unread_count,
    }

    return render(request, 'dashboard.html', context)

@login_required(login_url='admin_login')
def detailpage(request, id):
    user = get_object_or_404(Employee, id=id)
    users = Employee.objects.filter(id=id)

    if request.method == 'POST':
        # Update the fields in your Employee model based on checkbox values
        user.is_basic_details_verified = bool(request.POST.get('is_basic_details_verified', False))
        user.is_address_verified = bool(request.POST.get('is_address_verified', False))
        user.is_qualification_verified = bool(request.POST.get('is_qualification_verified', False))
        user.is_occupation_verified = bool(request.POST.get('is_occupation_verified', False))
        user.is_experience_verified = bool(request.POST.get('is_experience_verified', False))
        user.is_honors_verified = bool(request.POST.get('is_honors_verified', False))
        user.is_skillsets_verified = bool(request.POST.get('is_skillsets_verified', False))
        user.is_proofofwork_verified = bool(request.POST.get('is_proofofwork_verified', False))
        user.is_socialwork_verified = bool(request.POST.get('is_socialwork_verified', False))
        user.is_innovations_verified = bool(request.POST.get('is_innovations_verified', False))
        user.is_program_attend_verified = bool(request.POST.get('is_program_attend_verified', False))
        user.status = request.POST.get('status')

        user.save()  # Save the changes to the database

        return redirect('detailpage', id=id)

    return render(request, 'detailpage.html', {'users': users})


@login_required(login_url='admin_login')
def admin_logout(request):
    logout(request)
    messages.success(request,"successfully logged out")
    return redirect('admin_login')


@login_required(login_url='admin_login')
def note(request,id):
    # user = get_object_or_404(Employee, id=id)
    users = Employee.objects.filter(id=id)

    if request.method == 'POST':
        note = request.POST.get('note')
        employee = request.POST.get('employee')
        
        note = Note.objects.create(
            note = note,
            employee = employee,
        )
        note.save()

    return render(request, 'detailpage.html', {'users': users})


@login_required(login_url='admin_login')
def create_plan(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        discount = request.POST.get('discount')
        description = request.POST.get('description')

        plan = Level(
            name=name,
            price=price,
            discount=discount,
            description=description
        )
        plan.save()
        return redirect('plans')
    return render(request, 'create_plan.html')

@login_required(login_url='admin_login')
def plans(request):
    plans = Level.objects.all()
    return render(request,'plans.html',{'plans':plans})

@login_required(login_url='admin_login')
def companies(request):
    company = Company.objects.all()
    hr_list = HRUser.objects.all().order_by("-id")
    
    return render(request,'companies.html',{'company':company,'hr_list':hr_list})

@login_required(login_url='admin_login')
def approve_company(request, company_id):
    company = Company.objects.get(id=company_id)
    company.is_approved = True
    company.save()
    return redirect('companies')

@login_required(login_url='admin_login')
def approve_hr(request, hr_id):
    hr_user = HRUser.objects.get(id=hr_id)
    hr_user.is_approved = True
    hr_user.save()
    return redirect('hr_list')

@login_required(login_url='admin_login')
def insights(request):
    users = Employee.objects.all()
    company = Company.objects.all()
    hrs = HRUser.objects.all()


    unread_notifications = AdminNotification.objects.filter(user=request.user, is_read=False)

    # Calculate the count of unread notifications
    unread_count = unread_notifications.count()

    admin_notifications = AdminNotification.objects.filter(user=request.user)
    # print(notifications)
    verified_users = Employee.objects.filter(status='Verified')
    non_verified_users = Employee.objects.exclude(status='Verified')
    return render(request, 'insights.html',{'users':users,        'admin_notifications': admin_notifications,
        'unread_count': unread_count,'company':company,'hrs':hrs,'verified_users':verified_users,'non_verified_users':non_verified_users})


from django.template.loader import render_to_string

def filter_users(request):
    filter_option = request.GET.get('filter_option', '')
    users = Employee.objects.all()

    if filter_option == 'this_week':
        start_date = datetime.now() - timedelta(days=7)
        fusers = Employee.objects.filter(join_veriprofile_at__gte=start_date)
    elif filter_option == 'this_month':
        start_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        fusers = Employee.objects.filter(join_veriprofile_at__gte=start_date)
    elif filter_option == 'this_year':
        start_date = datetime.now().replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        fusers = Employee.objects.filter(join_veriprofile_at__gte=start_date)
    else:
        fusers = Employee.objects.all()

    # Render a partial HTML template with the filtered data
    filtered_users_html = render_to_string('insights.html', {'fusers': fusers,'users':users})

    return HttpResponse(filtered_users_html)


@login_required(login_url='admin_login')
def filter_data(request):
    # Default queryset: All employees
    users = Employee.objects.all()
    userlevels = UserLevel.objects.all()  # Assuming you have a UserLevel model


    if request.method == 'GET':
        filter_field = request.GET.get('filter_field')

        if filter_field:
            if filter_field == 'unique_id':
                unique_id_filter = request.GET.get('unique_id_filter')
                unique_id_value = request.GET.get('unique_id_search')

                if unique_id_value:
                    if unique_id_filter == 'exact':
                        users = users.filter(unique_id=unique_id_value)
                    else:
                        # Handle other unique_id filter conditions as needed
                        pass
            elif filter_field == 'Name':
                name_filter = request.GET.get('name_filter')
                name_search = request.GET.get('name_search')

                if name_filter == 'first_name':
                    users = users.filter(first_name__icontains=name_search)
                elif name_filter == 'last_name':
                    users = users.filter(last_name__icontains=name_search)
            elif filter_field == 'join_veriprofile_at':
                date_filter = request.GET.get('date_filter')
                date_filter_input = request.GET.get('date_filter_input')

                if date_filter_input:
                    try:
                        # Validate and parse the date
                        date_filter_input = datetime.strptime(date_filter_input, '%Y-%m-%d')
                        if date_filter == 'is':
                            users = users.filter(join_veriprofile_at=date_filter_input)
                        elif date_filter == 'above':
                            users = users.filter(join_veriprofile_at__gt=date_filter_input)
                        elif date_filter == 'below':
                            users = users.filter(join_veriprofile_at__lt=date_filter_input)
                    except ValueError:
                        # Handle invalid date format here
                        pass
            elif filter_field == 'profile_created_by':
                profile_created_by_filter = request.GET.get('profile_created_by_search')
                if profile_created_by_filter:
                    users = users.filter(profile_created_by__icontains=profile_created_by_filter)
            else:
                # Handle other filters as needed
                pass
    userlevels = userlevels.filter(user__in=users)


    context = {'users': users, 'userlevels': userlevels}
    return render(request, 'dashboard.html', context)



@login_required
def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(AdminNotification, pk=notification_id)

    # Check if the notification belongs to the logged-in admin
    if notification.user == request.user:
        notification.mark_as_read()

    return redirect('dashboard')

def daily_inspiration(request):
    if request.method == 'POST':
        images = request.FILES.getlist('images[]')

        for image in images:
            inspiration = DailyInspiration(image=image)
            inspiration.save()

        # Redirect to the same page after successful submission
        return redirect('daily_inspiration')

    inspirations = DailyInspiration.objects.all()
    
    return render(request, 'daily_inspiration.html', {'inspirations': inspirations})

def delete_inspiration(request, inspiration_id):
    inspiration = DailyInspiration.objects.get(id=inspiration_id)
    inspiration.delete()
    return JsonResponse({'message': 'Inspiration deleted successfully'})

# @login_required(login_url='admin_login')
# def notifications(request):
#     if request.method == 'POST':
#         # Get data from the form
#         notification_type = request.POST.get('notification_type')
#         notification_title = request.POST.get('notification_title')
#         frequency_option = request.POST.get('frequency_option')
#         message = request.POST.get('message')
#         link = request.POST.get('link')
#         schedule_date = request.POST.get('schedule_date')
#         recipients = request.POST.getlist('Recipients')

#         # Create notifications based on the selected recipients
#         employees = Employee.objects.all()
#         hr_users = HRUser.objects.all()

#         # Calculate scheduled_datetime outside the try block
#         scheduled_datetime = calculate_scheduled_datetime(frequency_option, schedule_date)

#         if scheduled_datetime is None:
#             messages.error(request, "No scheduled_datetime")
#             return redirect('notifications')

#         for recipient in recipients:
#             try:
#                 if recipient == 'hr_users':
#                     for hr_user in hr_users:
#                         broadcast_notification.apply_async(
#                             args=(None, notification_type, notification_title, message, link),
#                             eta=scheduled_datetime
#                         )
#                 elif recipient == 'Users':
#                     for employee in employees:
#                         broadcast_notification.apply_async(
#                             args=(employee.pk, notification_type, notification_title, message, link),
#                             eta=scheduled_datetime
#                         )
#             except Exception as e:
#                 messages.error(request, f"Error creating notification: {e}")

#     return render(request, 'notifications.html', {
#         # Your context data here
#     })

# def calculate_scheduled_datetime(frequency_option, schedule_date):
#     if not schedule_date:
#         return None

#     try:
#         # Convert schedule_date from string to datetime
#         schedule_date = datetime.strptime(schedule_date, '%Y-%m-%dT%H:%M')
#     except ValueError:
#         return None

#     scheduled_datetime = schedule_date  # Default to the provided schedule_date

#     if frequency_option == 'A Week':
#         scheduled_datetime += timedelta(weeks=1)
#     elif frequency_option == 'A Month':
#         scheduled_datetime += timedelta(days=30)  # Approximation
#     elif frequency_option == 'A Year':
#         scheduled_datetime += timedelta(days=365)  # Approximation
#     elif frequency_option == 'Hourly':
#         scheduled_datetime += timedelta(hours=1)
#     elif frequency_option.startswith('Custom'):
#         # Custom frequency, no specific calculation
#         pass

#     return scheduled_datetime

# def schedule_notification(request):
#     # Define the arguments for the task
#     employee_id = 1  # Replace with the actual employee ID
#     notification_type = "Informational"
#     notification_title = "Sample Title"
#     message = "This is a test message"
#     link = "https://example.com"
   
#     # Calculate the scheduled execution time (e.g., 5 minutes from now)
#     scheduled_time = datetime.now() + timedelta(minutes=5)

#     # Enqueue the task
#     broadcast_notification.apply_async(
#         args=(employee_id, notification_type, notification_title, message, link),
#         eta=scheduled_time
#     )
    
#     return HttpResponse("Scheduled a notification.")
