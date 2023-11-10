from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',views.home,name='home'),
    path('company_register/',views.company_register,name='company_register'),
    path('top_profiles_view/',views.top_profiles_view,name='top_profiles_view'),
    path('signin/',views.signin,name='signin'),
    path('quick_signup/',views.quick_signup,name='quick_signup'),
    path('personal_info_form/',views.personal_info_form,name='personal_info_form'),
    path('userdashboard/',views.userdashboard,name='userdashboard'),
    path('login_form/',views.temp_login,name='temp_login'),


    path('update_profile/<int:id>',views.update_profile,name='update_profile'),
    path('profile_data/<int:id>',views.profile_data_form,name='profile_data_form'),
    path('personal_details/<int:id>',views.personal_details,name='personal_details'),
    path('addresses/<int:id>',views.addresses,name='addresses'),
    path('qualification/<int:id>',views.qualification,name='qualification'),
    path('occupation/<int:id>',views.occupation,name='occupation'),
    path('experience/<int:id>',views.experience,name='experience'),
    path('honors_form/<int:id>',views.honors_form,name='honors_form'),
    path('skillset/<int:id>',views.skillset,name='skillset'),
    path('proof_of_works/<int:id>',views.proof_of_works,name='proof_of_works'),
    path('social_works/<int:id>',views.social_works,name='social_works'),
    path('other_act/<int:id>',views.other_act,name='other_act'),
    path('innovations/<int:id>',views.innovations,name='innovations'),




    path('wiki/in/<str:status>/<str:name>/<str:unique_id>',views.public_view,name='public_view'),
    path('notification/', views.notification, name='notification'),
    path('wiki/in/<str:status>/<str:name>/<str:code>/levels/', views.levels,name='levels'),
    path('verify_payment', views.verify_payment,name='verify_payment'),
    path('wiki/in/<str:status>/<str:name>/<str:code>/checkout/<int:id>', views.checkout,name='checkout'),
    path('signout/',views.signout,name='signout'),
    path('signout_home/',views.signout_home,name='signout_home'),
    path('success/',views.success,name='success'),
    path('fail/',views.fail,name='fail'),
    path('hr_register/',views.hr_register,name='hr_register'),
    path('hr_profile/',views.hr_profile,name='hr_profile'),
    path('backoffice/hr_login/',views.hr_login,name='hr_login'),
    path('backoffice/hr_panel/view_profiles/',views.view_profiles,name='view_profiles'),
    path('backoffice/hr_panel/insight/',views.insight,name='insight'),
    path('backoffice/hr_panel/verification_center/',views.verification_center,name='verification_center'),
    path('backoffice/hr_panel/assesment_center/',views.assesment_center,name='assesment_center'),
    path('hr_logout/', views.hr_logout, name='hr_logout'),
    path('add_media_reference/', views.add_media_reference, name='add_media_reference'),
    path('profile_view/', views.profile_view, name='profile_view'),
    path('backoffice/add_user/', views.add_user, name='add_user'),
    path('filtered_users/', views.filtered_users, name='filtered_users'),
    path('upload_cover/<str:employee_id>', views.upload_cover, name='upload_cover'),
    path('mark_as_read/<str:unique_id>', views.mark_as_read, name='mark_as_read'),
    path('pdf/', views.pdf, name='pdf'),
    path('user_gallery/', views.user_gallery, name='user_gallery'),

    path('token_send/', views.token_send, name='token_send'),
    path('verify/<auth_token>', views.verify, name='verify'),
    path('error/', views.error_page, name='verify'),
    path('test/', views.test, name='test'),
    

    # path('set/', views.setsession, name='setsession'),
    # path('get/', views.getsession, name='getsession'),
    # path('del/', views.delsession, name='getsession'),

    # path('set/', views.settestcookie, name='settestcookie'),
    # path('get/', views.checktestcookie, name='checktestcookie'),
    # path('del/', views.deltestcookie, name='deltestcookie'),

    # path('admin_notifications/', views.admin_notifications, name='admin_notifications'),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)




# def my_plans(request):
#     users = Employee.objects.filter(email=request.user.username)
#     user = get_object_or_404(User, email=request.user.email)
#     employee = get_object_or_404(Employee, email=user)    
#     userplans = UserLevel.objects.filter(user=employee)
#     return render(request,'my_plans.html',{'userplans':userplans,'users':users})