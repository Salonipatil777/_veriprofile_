from django.urls import path
from .views import *
from django.contrib.auth.views import LogoutView


urlpatterns = [  
    path('',admin_login,name='admin_login'),
    path('admin_logout/', admin_logout,name='admin_logout'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('users/', dashboard,name='dashboard'),
    path('create_plan/', create_plan,name='create_plan'),
    path('plans/', plans,name='plans'),
    path('companies/', companies,name='companies'),
    path('approve_company/<int:company_id>/', approve_company, name='approve_company'),
    path('approve_hr/<int:hr_id>/', approve_hr, name='approve_hr'),
    # path('checkout/', checkout,name='checkout'),
    path('verify_user/<int:id>',detailpage,name='detailpage'),
    path('note/<int:id>',note,name='note'),
    path('insights/',insights,name='insights'),
    path('filter_users/', filter_users, name='filter_users'),
    # path('notifications/', notifications, name='notifications'),
    # path('schedule_notification/', schedule_notification, name='schedule_notification'),
    path('daily_inspiration/', daily_inspiration, name='daily_inspiration'),
    path('filter_data/', filter_data, name='filter_data'),
    path('mark_notification_as_read/<int:notification_id>/', mark_notification_as_read, name='mark_notification_as_read'),
]

