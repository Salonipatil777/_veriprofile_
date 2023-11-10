import base64
from io import BytesIO
import random
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.messages import error,success
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from time import time
import razorpay
from veriprofile.settings import *
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
import requests
import uuid
from datetime import datetime
from .models import MediaReference
from django.utils import timezone
from PIL import Image
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.core.files.uploadedfile import InMemoryUploadedFile
from .forms import ImageForm
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from channels.layers import get_channel_layer


client = razorpay.Client(auth=(KEY_ID,KEY_SECRET))

from app.models import *
from customadmin.models import *

# Create your views here.
def home(request):
    levels = Level.objects.all()

    allemp = Employee.objects.all()
    return render(request,'home.html',{'levels':levels,'allemp':allemp})

def quick_signup(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        c_password = request.POST.get('c_password')
        unique_id = uuid.uuid4().hex[:8]

        # Create a new user
        user = User.objects.create_user(username, email, password)

        if Employee.objects.filter(username=username).exists():
            error(request, 'This username is already registered. Please use a different username.')
            return redirect('quick_signup') 
        if Employee.objects.filter(email=email).exists():
            error(request, 'This email is already registered. Please use a different email.')
            return redirect('quick_signup') 

        # Create an Employee instance but don't associate it with the user
        auth_token = str(uuid.uuid4())
        employee = Employee.objects.create(
            email=email,
            username=username,
            password=password,
            c_password=c_password,
            unique_id=unique_id,
            auth_token = auth_token
        )

        # Store the user's unique identifier in the session
        request.session['user_to_save'] = user.username
        send_mail_after_register(email,auth_token)
        return redirect('token_send')

    return render(request, 'quick_signup.html')

def personal_info_form(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        location = request.POST.get('location')
        contact = request.POST.get('contact')
        image_data_uri = request.POST.get('image', '')
        # cover_image = request.POST.get('cover_image')
        if image_data_uri:
            # Split the data URI into the content type and base64 data parts
            data_parts = image_data_uri.split(',')
            if len(data_parts) == 2:
                content_type, base64_data = data_parts
                try:
                    # Decode the base64 data into bytes
                    image_bytes = base64.b64decode(base64_data)
                    image_buffer = BytesIO(image_bytes)

                    # Open the image from the BytesIO buffer
                    img = Image.open(image_buffer)
                    img = img.resize((400, 400), Image.ANTIALIAS)

                    # Create a new BytesIO buffer to save the resized image
                    resized_buffer = BytesIO()
                    img.save(resized_buffer, format="JPEG")

                    # Create an InMemoryUploadedFile from the resized image buffer
                    img_file = InMemoryUploadedFile(
                        resized_buffer, None, 'image.jpg', 'image/jpeg', resized_buffer.tell(), None
                    )
                except Exception as e:
                    # Handle any exceptions that may occur during image processing
                    pass
        else:
            img_file = None

            
        # Retrieve the user's unique identifier from the session
        username = request.session.get('user_to_save')

        if username:
            # Retrieve the user object from the database based on the unique identifier (username)
            user = User.objects.get(username=username)

            # Create or retrieve the associated Employee instance and update the personal info
            try:
                employee = Employee.objects.get(username=username)
            except Employee.DoesNotExist:
                employee = Employee(unique_id=username)

            employee.first_name = first_name
            employee.last_name = last_name
            employee.location = location
            employee.contact = contact
            employee.image = img_file
            

            # Save the employee instance
            employee.save()

            # Clear the session variable
            del request.session['user_to_save']

            try:
                smart_level = Level.objects.get(name="Smart")
            except Level.DoesNotExist:
                smart_level = None
            else:
                # "Smart" level exists, create a UserLevel
                userlevel = UserLevel.objects.create(level=smart_level, user=employee)
                userlevel.save()

            # Redirect to a success page or do other processing as needed
            return redirect('temp_login')

    return render(request, 'personal_info_form.html')

def token_send(request):
    return render(request,'token_send.html')

def send_mail_after_register(email,token):
    subject = "Your account need to be verified"
    message = f'Hi paste the link to verify your account http://127.0.0.1:8000/verify/{token}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject,message,email_from,recipient_list)

def verify(request,auth_token):
    try:
        emp_obj = Employee.objects.filter(auth_token=auth_token).first()
        if emp_obj:
            if emp_obj.is_verified_email:
                return redirect('personal_info_form')
            emp_obj.is_verified_email = True

            emp_obj.save()
            # messages.success(request,"Email verified Successfully")
            return redirect('personal_info_form')
        else:
            return redirect('error')
    except Exception as e:
        print(e)

def error_page(request):
    return render(request,'error.html')

def update_profile(request,id):
    api_url = 'https://raw.githubusercontent.com/phillco/data/master/majors.json'
    response = requests.get(api_url)
    degrees_data = response.json()
    employee = Employee.objects.get(id=id)
    user = Employee.objects.filter(username=employee.username)
    id = id
    sociall = SocialLinks.objects.filter(employee=employee)
    qualification = Qualification.objects.filter(employee=employee)
    additional = AdditionalQualification.objects.filter(employee=employee)
    jobs = Jobs.objects.filter(employee=employee)
    experience = Experience.objects.filter(employee=employee)
    honors = Honors.objects.filter(employee=employee)
    skills = Skills.objects.filter(employee=employee)
    proofs = ProofOfWork.objects.filter(employee=employee)
    socialworks = SocialWork.objects.filter(employee=employee)
    innovationss = Innovation.objects.filter(employee=employee)
    media = MediaReferences.objects.filter(employee=employee)
    acts = OtherActivities.objects.filter(employee=employee)

    context = {
        'degrees': degrees_data,
        'user' : user,
        'sociall':sociall,
        'qualification':qualification,
        'additional':additional,
        'jobs':jobs,
        'experience':experience,
        'honors':honors,
        'skills':skills,
        'proofs':proofs,
        'socialworks':socialworks,
        'innovationss':innovationss,
        'media':media,
        'acts':acts,
    }

    return render(request, 'update_profile.html', context)

    # Define the process_and_save_image function

    # Define the process_and_save_image function

def upload_cover(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)

    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            form.save()  # The form handles cropping and saving the image
            # messages.success(request,"Image uploaded successfully")
            return redirect('userdashboard')
        else:
            return JsonResponse({'error': 'Invalid form data'}, status=400)

    form = ImageForm(instance=employee)
    return render(request, 'userdashboard.html', {'form': form, 'employee': employee})
  
def personal_details(request,id):
    employee = Employee.objects.get(id=id)
    user = Employee.objects.filter(username=employee.username)
    id = id

    if request.method == 'POST':
        salutation = request.POST.get('salutation')
        middle_name = request.POST.get('middle_name')
        gender = request.POST.get('gender')
        date_of_birth = request.POST.get('date_of_birth')
        marital_status = request.POST.get('marital_status')
        religion = request.POST.get('religion')
        nationality = request.POST.get('nationality')
        native_language = request.POST.get('native_language')
        languages_known = request.POST.get('languages_known')
        social_links = request.POST.getlist('social')
        facebook_links = request.POST.getlist('facebook')
        update_status = request.POST.get('update_status')

        employee.salutation=salutation
        employee.middle_name=middle_name
        employee.gender=gender
        employee.date_of_birth=date_of_birth
        employee.marital_status=marital_status
        employee.religion=religion
        employee.nationality=nationality
        employee.native_language=native_language
        employee.languages_known=languages_known
        # employee.social=social_link
        # employee.facebook=facebook
        if update_status == 'True':
            employee.update_status = True

        if social_links:
            # Loop through the lists and create SocialLinks instances
            for social, facebook in zip(social_links, facebook_links):
                social_link = SocialLinks(employee=employee, name=social, link=facebook)
                social_link.save()

        # messages.success(request,'Successfully Submit')
        employee.save()


    

    context = {
        'user' : user,
    }

    return render(request, 'update_profile.html', context)

def addresses(request,id):
    employee = Employee.objects.get(id=id)
    user = Employee.objects.filter(username=employee.username)
    id = id

    if request.method == 'POST':
        house_no = request.POST.get('house_no')
        street = request.POST.get('street')
        landmark = request.POST.get('landmark')
        country = request.POST.get('country')
        state = request.POST.get('state')
        city = request.POST.get('city')
        zip = request.POST.get('zip')

        home_country = request.POST.get('home_country')
        home_state = request.POST.get('home_state')
        home_city = request.POST.get('home_city')
        home_village = request.POST.get('home_village')
        home_zip = request.POST.get('home_zip')


        employee.house_no=house_no
        employee.street=street
        employee.landmark=landmark
        employee.country=country
        employee.state=state
        employee.city=city
        employee.zip=zip

        employee.home_country=home_country
        employee.home_state=home_state
        employee.home_city=home_city
        employee.home_village=home_village
        employee.home_zip=home_zip

        # messages.success(request,'Successfully Submit')
        employee.save()
    

    context = {
        'user' : user,
    }

    return render(request, 'update_profile.html', context)

def qualification(request, id):
    employee = Employee.objects.get(id=id)
    user = Employee.objects.filter(username=employee.username)
    id = id

    if request.method == 'POST':
        degrees = request.POST.getlist('degrees')
        specialization = request.POST.getlist('specialization')
        passing_year = request.POST.getlist('passing_year')
        college = request.POST.getlist('college')

        additional_info = request.POST.getlist('additional_info')
        additional_info_input = request.POST.getlist('additional_info_input')


        if degrees:
            # Loop through the lists and create Qualification instances
            for degree, spec, year,col in zip(degrees, specialization, passing_year,college):
                qualification = Qualification.objects.create(employee=employee, degree=degree, specialization=spec, passing_year=year,college=col)
                qualification.save()

        if additional_info:
            # Loop through the lists and create Qualification instances
            for additional, additional_in in zip(additional_info, additional_info_input):
                additional_info = AdditionalQualification.objects.create(employee=employee, name=additional, details=additional_in)
                additional_info.save()

        # Save the employee instance
        employee.save()

    context = {
        'user': user,
    }

    return render(request, 'update_profile.html', context)

def occupation(request,id):
    employee = Employee.objects.get(id=id)
    user = Employee.objects.filter(username=employee.username)
    id = id

    if request.method == 'POST':
        occupation_name = request.POST.get('occupation_name')
        job_title = request.POST.getlist('job_title')  # Update field name
        company_name = request.POST.getlist('company_name')  # Update field name
        joining_date = request.POST.getlist('joining_date')  # Update field name
        upload_id = request.FILES.getlist('upload_id')  # Update field name
        job_location = request.POST.getlist('job_location')  # Update field name
        job_industry = request.POST.getlist('job_industry')  # Update field name

        business_company_name = request.POST.get('business_company_name')
        industry = request.POST.get('industry')
        subcategory = request.POST.get('subcategory')
        formation_type = request.POST.get('formation_type')
        business_category = request.POST.get('business_category')
        business_start_date = request.POST.get('business_start_date')
        business_turnover = request.POST.get('business_turnover')
        business_country = request.POST.get('business_country')
        business_state = request.POST.get('business_state')
        business_city = request.POST.get('business_city')
        business_village = request.POST.get('business_village')
        business_zip = request.POST.get('business_zip')

        employee.occupation_name=occupation_name

        employee.business_company_name=business_company_name
        employee.industry=industry
        employee.subcategory=subcategory
        employee.formation_type=formation_type
        employee.business_category=business_category
        employee.business_start_date=business_start_date
        employee.business_turnover=business_turnover
        employee.business_country=business_country
        employee.business_state=business_state
        employee.business_city=business_city
        employee.business_village=business_village
        employee.business_zip=business_zip

        if job_title:
            for jobtitle, comp, joining,upload,locate,jIndustry in zip(job_title, company_name, joining_date,upload_id,job_location,job_industry):
                job = Jobs.objects.create(
                    employee=employee,
                    job_title=jobtitle,
                    company_name=comp,
                    joining_date=joining,
                    upload_id=upload,
                    job_location=locate,
                    job_industry=jIndustry,
                )
                job.save()


        # messages.success(request,'Successfully Submit')
        employee.save()
    

    context = {
        'user' : user,
    }

    return render(request, 'update_profile.html', context)

def experience(request,id):
    employee = Employee.objects.get(id=id)
    user = Employee.objects.filter(username=employee.username)
    id = id
    

    if request.method == 'POST':
        ex_job_title = request.POST.getlist('ex_job_title')
        ex_company_name = request.POST.getlist('ex_company_name')
        ex_joining_date = request.POST.getlist('ex_joining_date')
        ex_quit_date = request.POST.getlist('ex_quit_date')
        ex_upload_id = request.FILES.getlist('ex_upload_id')  # Update field name
        ex_job_location = request.POST.getlist('ex_job_location')
        ex_job_industry = request.POST.getlist('ex_job_industry')


        if ex_job_title:
            for exjobtitle, excomp, exjoining,exquit,exupload,exlocation,exIndustry in zip(ex_job_title, ex_company_name, ex_joining_date,ex_quit_date,ex_upload_id,ex_job_location,ex_job_industry):
                exjob = Experience.objects.create(
                    employee=employee,
                    ex_job_title=exjobtitle,
                    ex_company_name=excomp,
                    ex_joining_date=exjoining,
                    ex_quit_date=exquit,
                    ex_upload_id=exupload,
                    ex_job_location=exlocation,
                    ex_job_industry=exIndustry,
                )
                exjob.save()


        # messages.success(request,'Successfully Submit')
        employee.save()
        
    

    context = {
        'user' : user,
        
    }

    return render(request, 'update_profile.html', context)

def honors_form(request,id):
    employee = Employee.objects.get(id=id)
    user = Employee.objects.filter(username=employee.username)
    id = id
    

    if request.method == 'POST':
        honors = request.POST.getlist('honors')
        honor_type = request.POST.getlist('honor_type')
        awards_name = request.POST.getlist('awards_name')
        awards_given_by = request.POST.getlist('awards_given_by')


        if honors:
            # Loop through the lists and create SocialLinks instances
            for honor, honorsType,award,award_by in zip(honors, honor_type,awards_name,awards_given_by):
                honor_save = Honors(employee=employee, honors=honor, honor_type=honorsType,awards_name=award,awards_given_by=award_by)
                honor_save.save()


        # messages.success(request,'Successfully Submit')
        employee.save()
        
    

    context = {
        'user' : user,
        
    }

    return render(request, 'update_profile.html', context)

def skillset(request,id):
    employee = Employee.objects.get(id=id)
    user = Employee.objects.filter(username=employee.username)
    id = id
    

    if request.method == 'POST':
        skill_name = request.POST.getlist('skill_name')
        skill_filed = request.POST.getlist('skill_filed')

        if skill_name:
            # Loop through the lists and create SocialLinks instances
            for skill, field in zip(skill_name, skill_filed):
                skill_save = Skills(employee=employee, skill_name=skill, skill_filed=field)
                skill_save.save()


        # messages.success(request,'Successfully Submit')
        employee.save()
    

    context = {
        'user' : user,
        
    }

    return render(request, 'update_profile.html', context)

def proof_of_works(request,id):
    employee = Employee.objects.get(id=id)
    user = Employee.objects.filter(username=employee.username)
    id = id
    

    if request.method == 'POST':
        proof_of_work = request.POST.getlist('proof_of_work')
        proof_of_work_input = request.POST.getlist('proof_of_work_input')
        name = request.POST.getlist('name')
        link = request.POST.getlist('link')

        if proof_of_work:
            # Loop through the lists and create SocialLinks instances
            for proof, proof_link in zip(proof_of_work, proof_of_work_input):
                proof_save = ProofOfWork(employee=employee, proof_of_work=proof, proof_of_work_input=proof_link)
                proof_save.save()

        if name:
            # Loop through the lists and create SocialLinks instances
            for nm, lk in zip(name, link):
                media = MediaReferences(employee=employee, name=nm, link=lk)
                media.save()

        # messages.success(request,'Successfully Submit')
        employee.save()
        
    

    context = {
        'user' : user,
        
    }

    return render(request, 'update_profile.html', context)

def social_works(request,id):
    employee = Employee.objects.get(id=id)
    user = Employee.objects.filter(username=employee.username)
    id = id
    

    if request.method == 'POST':
        social_work = request.POST.getlist('social_work')
        social_work_input = request.POST.getlist('social_work_input')

        if social_work:
            # Loop through the lists and create SocialLinks instances
            for socialwork, socialworkinput in zip(social_work, social_work_input):
                social_save = SocialWork(employee=employee, social_work=socialwork, social_work_input=socialworkinput)
                social_save.save()


        # messages.success(request,'Successfully Submit')
        employee.save()
        
    

    context = {
        'user' : user,
        
    }

    return render(request, 'update_profile.html', context)

def innovations(request,id):
    employee = Employee.objects.get(id=id)
    user = Employee.objects.filter(username=employee.username)
    id = id
    

    if request.method == 'POST':
        innovation_name = request.POST.getlist('innovation_name')
        proof_of_concept = request.POST.getlist('proof_of_concept')
        upload_info_video = request.FILES.getlist('upload_info_video')
        upload_info_image = request.FILES.getlist('upload_info_image')
        date_of_inovation = request.POST.getlist('date_of_inovation')
        upload_info_certificate = request.FILES.getlist('upload_info_certificate')
        innovation_link = request.POST.getlist('innovation_link')
        reference_name = request.POST.getlist('reference_name')
        reference_contact = request.POST.getlist('reference_contact')

        if innovation_name:
            for innoName, innoConcept, infoVid,infoImg,dataInven,infocer,innoLink,refName,refCon in zip(innovation_name, proof_of_concept, upload_info_video,upload_info_image,date_of_inovation,upload_info_certificate,innovation_link,reference_name,reference_contact):
                innovation = Innovation.objects.create(
                    employee=employee,
                    innovation_name=innoName,
                    proof_of_concept=innoConcept,
                    upload_info_video=infoVid,
                    upload_info_image=infoImg,
                    date_of_inovation=dataInven,
                    upload_info_certificate=infocer,
                    innovation_link=innoLink,
                    reference_name=refName,
                    reference_contact=refCon,
                )
                innovation.save()



        # messages.success(request,'Successfully Submit')
        employee.save()
        
    

    context = {
        'user' : user,
        
    }

    return render(request, 'update_profile.html', context)

def other_act(request,id):
    employee = Employee.objects.get(id=id)
    user = Employee.objects.filter(username=employee.username)
    id = id
    

    if request.method == 'POST':
        act_type = request.POST.getlist('act_type')
        act_title = request.POST.getlist('act_title')
        act_link = request.POST.getlist('act_link')
        act_date = request.POST.getlist('act_date')

        if act_type:
            # Loop through the lists and create SocialLinks instances
            for actType, actTitle,actLink,actDate in zip(act_type, act_title,act_link,act_date):
                act_save = OtherActivities(employee=employee, act_type=actType, act_title=actTitle,act_link=actLink,act_date=actDate)
                act_save.save()


        # messages.success(request,'Successfully Submit')
        employee.save()
        
    

    context = {
        'user' : user,
        
    }

    return render(request, 'update_profile.html', context)

def signin(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username_or_email')
        password = request.POST.get('password')

        if not username_or_email:
            error(request, "Please enter a username or email.")
            return redirect('temp_login')

        if not password:
            error(request, "Please enter a password.")
            return redirect('temp_login')

        user = authenticate(request, username=username_or_email, password=password)

        if user is not None:
            emp_obj = Employee.objects.filter(username=user.username).first()
            if not emp_obj.is_verified_email:
                error(request, "Your email is not verified")
                return redirect('temp_login')

            login(request, user)
            return redirect('userdashboard')
        else:
            # Check if the username exists in the database
            if not Employee.objects.filter(password=password).exists():
                error(request, "Invalid username or password. Please try again.")
            return redirect('temp_login')

    return render(request, 'temp_loginform.html')

def profile_data_form(request,id):
    api_url = 'https://raw.githubusercontent.com/phillco/data/master/majors.json'
    response = requests.get(api_url)
    degrees_data = response.json()
    employee = Employee.objects.get(id=id)
    user = Employee.objects.filter(username=employee.username)
    id = id


    context = {
        'degrees': degrees_data,
        'user' : user,
    }

    return render(request,'profile_data_form.html',context)

@login_required(login_url='signin')
def userdashboard(request):
    users = get_object_or_404(User, username=request.user.username)
    employee = get_object_or_404(Employee, username=users)  
    userr = Employee.objects.filter(username=employee.username)

    note = Note.objects.filter(employee=request.user.username)
    current_url = request.build_absolute_uri()
    facebook_share_url = f"https://www.facebook.com/send?text={current_url}"
    twitter_share_url = f"https://twitter.com/intent/send?text={current_url}"
    whatsapp_share_link = f"https://api.whatsapp.com/send?text={current_url}"
    instagram_share_link = f"https://www.instagram.com/share?text={current_url}"


    users = get_object_or_404(User, username=request.user.username)
    employee = get_object_or_404(Employee, username=users)    
    userlevels = UserLevel.objects.filter(user=employee)
    

    qualifications = Qualification.objects.filter(employee=employee)
    advance = AdditionalQualification.objects.filter(employee=employee)
    experiences = Experience.objects.filter(employee=employee)
    skills = Skills.objects.filter(employee=employee)
    awards = Honors.objects.filter(employee=employee)
    works = ProofOfWork.objects.filter(employee=employee)
    social_work = SocialWork.objects.filter(employee=employee)
    media = MediaReferences.objects.filter(employee=employee)
    acts = OtherActivities.objects.filter(employee=employee)
    
    experience_data = []

    for experience in experiences:
        joining_date = datetime.strptime(experience.ex_joining_date, '%Y-%m-%d')
        quit_date = datetime.strptime(experience.ex_quit_date, '%Y-%m-%d')

        # Calculate the experience for this specific job
        job_experience = quit_date - joining_date
        years_of_experience = job_experience.days // 365
        months_of_experience = (job_experience.days % 365) // 30

        # Calculate the fractional experience for this job
        fractional_experience = years_of_experience + (months_of_experience / 12)

        # Add the fractional experience to the experience data
        experience_data.append({
            'experience': fractional_experience,
            'total_experience_years': years_of_experience,
            'total_experience_months': months_of_experience,
            'ex_job_title': experience.ex_job_title,
            'ex_company_name': experience.ex_company_name,
            'ex_job_location': experience.ex_job_location,
            'ex_job_industry': experience.ex_job_industry,
            'ex_joining_date': experience.ex_joining_date,
            'ex_quit_date': experience.ex_quit_date,
        })

    # Get gallery and daily inspiration data
    gallery = Gallery.objects.filter(user=employee).order_by('-id')
    daily_inspiration = DailyInspiration.objects.all().order_by('-id')
    random_image = random.choice(daily_inspiration) if daily_inspiration else None

    today = timezone.now().date()

    user_messages = Ping.objects.filter(user=employee).order_by('-id')
    unread_messages = user_messages.filter(read_status=False)
    message_count = unread_messages.count()  

    if request.method == 'POST':
        sender = get_object_or_404(User, username=request.user.username)
        emp = get_object_or_404(Employee, username=sender)

        message = request.POST.get('message')

        # Assuming you're getting user_messages as a QuerySet, you need to loop through it
        for user_message in user_messages:
            receiver = Employee.objects.get(email=user_message.sender.email)

            ping = Ping.objects.create(
                message=message,
                sender=emp,
                user=receiver,  # Associate the message with the specific user
            )
            ping.save()    

    # user_notifications = Notification.objects.filter(users=employee).order_by('-id')
    # unread_notifications = user_notifications.filter(read_status=False)
    # notification_count = unread_notifications.count()  

    allemp = Employee.objects.all()

    return render(request,'userdashboard.html',{'userr':userr,'note':note,'facebook_share_url': facebook_share_url,
    'twitter_share_url': twitter_share_url,'gallery':gallery,'daily_inspiration':daily_inspiration,'instagram_share_link': instagram_share_link,'whatsapp_share_link': whatsapp_share_link,'userlevels':userlevels,'random_image': random_image,'today': today,'qualifications':qualifications,'advance':advance,
    'experience_data': experience_data, 'experiences': experiences,'experiences':experiences,'skills':skills,'awards':awards,'works':works,'social_work':social_work,'media':media,'acts':acts,'message_count':message_count,'user_messages':user_messages,'allemp':allemp,'room_name':"broadcast"
})

@login_required(login_url='signin')
def notification(request):
    userr = Employee.objects.filter(username=request.user.username)
    daily_inspiration = DailyInspiration.objects.all().order_by('-id')
    users = get_object_or_404(User, username=request.user.username)
    employee = get_object_or_404(Employee, username=users)   

    # user_notifications = Notification.objects.filter(users=employee).order_by('-id')
    # unread_notifications = user_notifications.filter(read_status=False)
    # notification_count = unread_notifications.count()   

    if request.method == 'POST':
        # Mark all notifications as read
        # user_notifications.update(read_status=True)
        # Redirect back to the notifications page or any other desired page
        return redirect('notification')

    user_messages = Ping.objects.filter(user=employee).order_by('-id')
    unread_messages = user_messages.filter(read_status=False)
    message_count = unread_messages.count()  

    if request.method == 'POST':
        sender = get_object_or_404(User, email=request.user.email)
        emp = get_object_or_404(Employee, email=sender)

        message = request.POST.get('message')

        # Assuming you're getting user_messages as a QuerySet, you need to loop through it
        for user_message in user_messages:
            receiver = Employee.objects.get(email=user_message.sender.email)

            ping = Ping.objects.create(
                message=message,
                sender=emp,
                user=receiver  # Associate the message with the specific user
            )
            ping.save()

    return render(request, 'all_notifications.html', {
        'userr': userr,
        'daily_inspiration': daily_inspiration,
        'user_messages':user_messages,'message_count':message_count
    })

def public_view(request, status, unique_id, name):
    # Assuming 'unique_id' is unique and identifies a single user
    userr = Employee.objects.filter(unique_id=unique_id)
    userr2 = Employee.objects.get(unique_id=unique_id)
    name = name
    status = status
    current_url = request.build_absolute_uri()
    facebook_share_url = f"https://www.facebook.com/send?text={current_url}"
    twitter_share_url = f"https://twitter.com/intent/send?text={current_url}"
    whatsapp_share_link = f"https://api.whatsapp.com/send?text={current_url}"
    instagram_share_link = f"https://www.instagram.com/share?text={current_url}"
    daily_inspiration = DailyInspiration.objects.all().order_by('-id')
    # users = Employee.objects.filter(unique_id=unique_id)
    # users_level = UserLevel.objects.filter(user=user)
    # Get the current user's enrolled levels
    sender = get_object_or_404(User, username=request.user.username)
    # emp = get_object_or_404(Employee, username=sender)


    reciever = get_object_or_404(Employee, unique_id=unique_id)


    gallery = Gallery.objects.filter(user=userr2).order_by('-id')

    qualifications = Qualification.objects.filter(employee=userr2)
    advance = AdditionalQualification.objects.filter(employee=userr2)
    experiences = Experience.objects.filter(employee=userr2)
    skills = Skills.objects.filter(employee=userr2)
    awards = Honors.objects.filter(employee=userr2)
    
    experience_data = []

    for experience in experiences:
        joining_date = datetime.strptime(experience.ex_joining_date, '%Y-%m-%d')
        quit_date = datetime.strptime(experience.ex_quit_date, '%Y-%m-%d')

        # Calculate the experience for this specific job
        job_experience = quit_date - joining_date
        years_of_experience = job_experience.days // 365
        months_of_experience = (job_experience.days % 365) // 30

        # Calculate the fractional experience for this job
        fractional_experience = years_of_experience + (months_of_experience / 12)

        # Add the fractional experience to the experience data
        experience_data.append({
            'experience': fractional_experience,
            'total_experience_years': years_of_experience,
            'total_experience_months': months_of_experience,
            'ex_job_title': experience.ex_job_title,
            'ex_company_name': experience.ex_company_name,
            'ex_job_location': experience.ex_job_location,
            'ex_job_industry': experience.ex_job_industry,
            'ex_joining_date': experience.ex_joining_date,
            'ex_quit_date': experience.ex_quit_date,
        })


    # Get gallery and daily inspiration data
    daily_inspiration = DailyInspiration.objects.all().order_by('-id')
    random_image = random.choice(daily_inspiration) if daily_inspiration else None

    today = timezone.now().date()

    
    if request.method == 'POST':
        message = request.POST.get('message')

        ping = Ping.objects.create(
            message=message,
            sender = sender,
            user=reciever  # Associate the message with the specific user
        )

        ping.save()

    return render(request, 'public_view.html', {
    'userr': userr,
    'facebook_share_url': facebook_share_url,
    'twitter_share_url': twitter_share_url,
    'instagram_share_link': instagram_share_link,
    'whatsapp_share_link': whatsapp_share_link,
    'daily_inspiration': daily_inspiration,
    'gallery': gallery,
    'daily_inspiration': daily_inspiration,
    'instagram_share_link': instagram_share_link,
    'whatsapp_share_link': whatsapp_share_link,
    'random_image': random_image,
    'today': today,
    'qualifications': qualifications,
    'advance': advance,
    'experience_data': experience_data,  # Use 'experience_data' instead of 'experience'
    'experiences': experiences,
    'skills': skills,
    'awards': awards,
})

def mark_as_read(request,unique_id):
    user = Employee.objects.filter(unique_id=unique_id)
    if request.method == 'POST':
        message_id = request.POST.get('message_id')
        message = Ping.objects.get(pk=message_id)
        message.read_status = True
        message.save()
        return redirect('userdashboard')

        # You can perform additional actions if needed

    return render(request,'public_view.html')  # Return an appropriate response

@login_required(login_url='signin')
def levels(request, status, name, code):
    users = Employee.objects.filter(username=request.user.username)
    levels = Level.objects.all()

    status = status
    code = code
    name = name

    # Get the current user's enrolled levels
    user = get_object_or_404(User, username=request.user.username)
    employee = get_object_or_404(Employee, username=user)    
    # user = get_object_or_404(User, email=request.user.email)
    enrolled_levels = UserLevel.objects.filter(user=employee).values_list('level_id', flat=True)

    # Get gallery and daily inspiration data
    gallery = Gallery.objects.filter(user=employee).order_by('-id')
    daily_inspiration = DailyInspiration.objects.all().order_by('-id')
    random_image = random.choice(daily_inspiration) if daily_inspiration else None

    today = timezone.now().date()


    # user_notifications = Notification.objects.filter(users=employee).order_by('-id')
    # unread_notifications = user_notifications.filter(read_status=False)
    # notification_count = unread_notifications.count()



    user_messages = Ping.objects.filter(user=employee).order_by('-id')
    unread_messages = user_messages.filter(read_status=False)
    message_count = unread_messages.count()  

    if request.method == 'POST':
        sender = get_object_or_404(User, username=request.user.username)
        emp = get_object_or_404(Employee, username=sender)

        message = request.POST.get('message')

        # Assuming you're getting user_messages as a QuerySet, you need to loop through it
        for user_message in user_messages:
            receiver = Employee.objects.get(email=user_message.sender.email)

            ping = Ping.objects.create(
                message=message,
                sender=emp,
                user=receiver,  # Associate the message with the specific user
            )
            ping.save()    


    allemp = Employee.objects.all()
    

    # unread_notifications = user_notifications.filter(read_status=False)
    # notification_count = unread_notifications.count()   
    return render(request, 'levels.html', {'daily_inspiration':daily_inspiration, 'levels': levels, 'users': users, 'enrolled_levels': enrolled_levels,'message_count':message_count,'user_messages':user_messages,'today':today,'random_image':random_image,'gallery':gallery,'allemp':allemp})

@csrf_exempt
def checkout(request,id, status, name, code):
    level = get_object_or_404(Level, id=id)
    user = get_object_or_404(Employee, username=request.user.username)
    users = Employee.objects.filter(username=request.user.username)

    n_user = get_object_or_404(User, username=request.user.username)
    employee = get_object_or_404(Employee, username=n_user)    

    status = status
    code = code
    name = name
    action = request.GET.get('action')

    # user_notifications = Notification.objects.filter(users=employee).order_by('-id')
    # unread_notifications = user_notifications.filter(read_status=False)
    # notification_count = unread_notifications.count()   
    order = None
    if level.price == 0:
        user_level = UserLevel(
            user=user,
            level=level,
        )
        user_level.save()
        return redirect('home')
    elif action == 'create_payment':
        if request.method == "POST":
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            country = request.POST.get('country')
            address_1 = request.POST.get('address_1')
            address_2 = request.POST.get('address_2')
            city = request.POST.get('city')
            state = request.POST.get('state')
            postcode = request.POST.get('postcode')
            phone = request.POST.get('phone')
            email = request.POST.get('email')
            order_comments = request.POST.get('order_comments')

            amount_cal = level.price
            amount = int(amount_cal) * 100
            currency = "INR"
            notes={
                "name" : f'{first_name} {last_name}',
                "country" : country,
                "address" : f'{address_1} {address_2}',
                "city" : city,
                "state" : state,
                "postcode" : postcode,
                "phone" : phone,
                "email" : email,
                "order_comments" : order_comments,
            }
            receipt = f"Skola-{int(time())}"
            order = client.order.create(
                {
                    'receipt' :receipt,
                    'notes' : notes,
                    'amount' : amount,
                    'currency' : currency,
                }
            )

            user = get_object_or_404(User, username=request.user.username)
            employee = get_object_or_404(Employee, username=user)
            payment = Payment(
                level=level,
                user = employee,
                order_id = order.get('id'),
            )
            payment.save()

    
    context = {
        'level': level,
        'order': order,
        'user':user,
        'users':users,
        # 'user_notifications': user_notifications,
        # 'notification_count':notification_count, 
    }
    
        
    return render(request,'checkout.html',context)

@login_required(login_url='signin')
def signout(request):
    if request.user.is_authenticated:
        # Record the logout time
        user = get_object_or_404(User, username=request.user.username)
        employee = get_object_or_404(Employee, username=user)    
        login_history = LoginHistory.objects.filter(user=employee).first()
        if login_history:
            login_history.logout_time = timezone.now()
            login_history.save()
        else:
            # If no record exists, create a new one
            LoginHistory.objects.create(user=employee, logout_time=timezone.now())
    # Call the built-in logout function to log the user out
    logout(request)

    # success(request,"successfully logged out")
    return redirect('temp_login')

def signout_home(request):
    if request.user.is_authenticated:
     logout(request)

    # success(request,"successfully logged out")
    return redirect('signin')

@csrf_exempt
def verify_payment(request):
    if request.method == "POST":
        data = request.POST
        try:
            client.utility.verify_payment_signature(data)
            razorpay_order_id = data['razorpay_order_id']
            razorpay_payment_id = data['razorpay_order_id']

            payment = Payment.objects.get(order_id=razorpay_order_id)
            payment.payment_id = razorpay_payment_id
            payment.status = True
            payment.save()  # Save the changes to the Payment object

            # Check if a UserLevel instance for the user already exists
            try:
                user_levels = UserLevel.objects.get(user=payment.user)
                # If it exists, update its attributes
                user_levels.user = payment.user
                user_levels.level = payment.level
                user_levels.save()
            except UserLevel.DoesNotExist:
                # If it doesn't exist, create a new UserLevel
                user_levels = UserLevel(user=payment.user, level=payment.level)
                user_levels.save()

            context = {
                'data': data,
                'payment': payment,
            }
            return redirect('success')
        except:
            return redirect('fail')

def success(request):
    users = Employee.objects.filter(username=request.user.username)
    user = get_object_or_404(User, username=request.user.username)
    employee = get_object_or_404(Employee, username=user)
    return render(request, 'success.html',{'users':users,'employee':employee})

def fail(request):
    return render(request, 'fail.html')

def company_register(request):
    if request.method == 'POST':
        name_of_partner = request.POST.get('name_of_partner')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        address = request.POST.get('address')
        industry_field = request.POST.get('industry_field')

        nature_of_partenership = request.POST.getlist('nature_of_partenership')
        duration_of_partenership = request.POST.get('duration_of_partenership')

        select_by_requirements = request.POST.getlist('select_by_requirements')
        select_by_level = request.POST.getlist('select_by_level')
        number_of_candidates = request.POST.get('number_of_candidates')

        technical_point_of_contact = request.POST.get('technical_point_of_contact')
        do_you_need_api = request.POST.get('do_you_need_api')

        data_sharing = request.FILES.get('data_sharing')

        data_retention_policy = request.POST.get('data_retention_policy')

        responsibilities = bool(request.POST.get('responsibilities', False))
        partnership_agreement = bool(request.POST.get('partnership_agreement', False))
        
        requests_for_requirements = request.POST.get('requests_for_requirements')
        additional_doc = request.POST.get('additional_doc')

        company = Company.objects.create(
            name_of_partner=name_of_partner,
            phone=phone,
            email=email,
            address=address,
            industry_field=industry_field,
            nature_of_partenership=nature_of_partenership,
            duration_of_partenership=duration_of_partenership,
            select_by_requirements=select_by_requirements,
            select_by_level=select_by_level,
            number_of_candidates=number_of_candidates,
            technical_point_of_contact=technical_point_of_contact,
            do_you_need_api=do_you_need_api,
            data_sharing=data_sharing,
            data_retention_policy=data_retention_policy,
            responsibilities=responsibilities,
            partnership_agreement=partnership_agreement,
            requests_for_requirements=requests_for_requirements,
            additional_doc=additional_doc,
            )
            # messages.success(request,'Successfully Submit')
        company.save()
        return redirect('hr_register')



    return render(request, 'company_register.html')

def hr_login(request):
    # if request.method == 'POST':
    #     username = request.POST.get('username')
    #     password = request.POST.get('password')
    #     try:
    #         registration_model = HRUser.objects.get(username=username)
    #     except HRUser.DoesNotExist:
    #         registration_model = None
    #     if registration_model and registration_model.password == password:
    #         return redirect('hr_panel' ,username)
    #     else:
    #         error(request,"username or password not correct")
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('insight')
        else:
            error(request,"username or password not correct")
            return redirect('signin')
    return render(request, 'signin.html')

def hr_logout(request):
    logout(request)
    return redirect('signin')

def hr_register(request):
    company = Company.objects.all()
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        company_name = request.POST.get('company_name')
        address_hr = request.POST.get('address_hr')
        designation_in_company = request.POST.get('designation_in_company')
        hr_email = request.POST.get('hr_email')
        contact = request.POST.get('contact')
        employment_number = request.POST.get('employment_number')
        employment_id = request.FILES.get('employment_id')
        username = request.POST.get('username')
        password = request.POST.get('password')
        aadhar_card = request.FILES.get('aadhar_card')


        if username == '' or password == '':
            error(request, 'Username and password must be required')
            return redirect('hr_register')
        
         # Check if the email already exists in the database
        if HRUser.objects.filter(username=username).exists():
            error(request, 'This username is already registered. Please use a different username.')
            return redirect('hr_register')  # Redirect to the 'register' URL name or any other registration page
        
        comp = get_object_or_404(Company, name_of_partner=company_name)

        user = User.objects.create_user(username,hr_email,password)
        user = User.objects.get(email=hr_email)
        hr_user = HRUser.objects.create(
            first_name=first_name,
            last_name=last_name,
            company_name=comp,
            address_hr=address_hr,
            designation_in_company=designation_in_company,
            hr_email=hr_email,
            contact=contact,
            employment_number=employment_number,
            employment_id=employment_id,
            aadhar_card=aadhar_card,
            username=username,
            password=password,
        )
        hr_user.save()
        user.save()
        return redirect('signin')

    return render(request, 'hr_register.html',{'company':company})

def top_profiles_view(request):
    top_profiles = Employee.objects.top_profiles(num_profiles=10)  # Adjust the number as needed
    return render(request, 'top_profiles.html', {'top_profiles': top_profiles})

def add_media_reference(request):
    if request.method == 'POST':
        # Get the number of input fields based on the submitted data
        num_inputs = len([key for key in request.POST if key.startswith('reference_link_')])

        for i in range(num_inputs):
            reference_link = request.POST.get(f'reference_link_{i}')
            info = MediaReference.objects.create(
                reference_link=reference_link
            )
            info.save()

        return redirect('profile_view')

    return render(request, 'add_media_reference.html')

def profile_view(request):
    media_references = MediaReference.objects.all()
    return render(request, 'profile_view.html', {'media_references': media_references})

@login_required(login_url='hr_login')
def add_user(request):
    hr_user = HRUser.objects.get(username=request.user.username)
    print(hr_user)
    api_url = 'https://raw.githubusercontent.com/jneidel/job-titles/master/job-titles.json'
    response = requests.get(api_url)
    job_titles_data = response.json().get('job-titles', [])

    context = {
        'job_titles': job_titles_data,
        'hr_user':hr_user,
    }

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        middle_name = request.POST.get('middle_name')
        last_name = request.POST.get('last_name')
        gender = request.POST.get('gender')
        marital_status = request.POST.get('marital_status')
        date_of_birth = request.POST.get('date_of_birth')
        nationality = request.POST.get('nationality')
        religion = request.POST.get('religion')
        preferred_language = request.POST.get('preferred_language')
        languages_known = request.POST.get('languages_known')
        wikipedia = request.POST.get('wikipedia')
        personal_website = request.POST.get('personal_website')
        email = request.POST.get('email')
        password = request.POST.get('password')
        mobile = request.POST.get('mobile')
        time_zone = request.POST.get('time_zone')
        address = request.POST.get('address')
        facebook = request.POST.get('facebook')
        ted = request.POST.get('ted')
        youtube = request.POST.get('youtube')
        linkedin = request.POST.get('linkedin')
        degrees = request.POST.get('degrees')
        institutions_attended = request.POST.get('institutions_attended')
        gpa_academic_achivements = request.POST.get('gpa_academic_achivements')
        graduation_dates = request.POST.get('graduation_dates')
        job_title = request.POST.get('job_title')
        company = request.POST.get('company')
        industry = request.POST.get('industry')
        joining_date = request.POST.get('joining_date')
        job_location = request.POST.get('job_location')
        job_title1 = request.POST.get('job_title1')
        joining_date1 = request.POST.get('joining_date1')
        quit_date = request.POST.get('quit_date')
        company_name = request.POST.get('company_name')
        industry_name = request.POST.get('industry_name')
        location = request.POST.get('location')
        role = request.POST.get('role')
        responsibilities = request.POST.get('responsibilities')
        certifications = request.POST.get('certifications')
        licenses = request.POST.get('licenses')
        awards = request.POST.get('awards')
        publications = request.POST.get('publications')
        researches = request.POST.get('researches')
        projects = request.POST.get('projects')
        portfolio = request.POST.get('portfolio')
        project_link1 = request.POST.get('project_link1')
        project_link2 = request.POST.get('project_link2')
        project_link3 = request.POST.get('project_link3')
        volunteer_work = request.POST.get('volunteer_work')
        professional_memberships = request.POST.get('professional_memberships')
        availability_for_networking = request.POST.get('availability_for_networking')
        technical_skills = request.POST.get('technical_skills')
        soft_skills = request.POST.get('soft_skills')
        languages_spoken = request.POST.get('languages_spoken')
        hobbies = request.POST.get('hobbies')
        causes_and_interest = request.POST.get('causes_and_interest')
        contact_information = request.POST.get('contact_information')
        published_articles = request.POST.get('published_articles')
        gitHub_repository_links = request.POST.get('gitHub_repository_links')
        open_source_contributions = request.POST.get('open_source_contributions')
        case_studies = request.POST.get('case_studies')
        whitepapers = request.POST.get('whitepapers')
        research_papers = request.POST.get('research_papers')
        artifacts_or_creative_works = request.POST.get('artifacts_or_creative_works')
        project_demonstrations_or_Videos = request.POST.get('project_demonstrations_or_Videos')
        Patents_or_intellectual_property = request.POST.get('Patents_or_intellectual_property')
        testimonials_or_recommendations = request.POST.get('testimonials_or_recommendations')
        Open_Source_Projects = request.POST.get('Open_Source_Projects')
        links_to_gitHub = request.POST.get('links_to_gitHub')
        open_source_organizations_joined = request.POST.get('open_source_organizations_joined')
        conference_talks = request.POST.get('conference_talks')
        webinar_presentations = request.POST.get('webinar_presentations')
        workshop_facilitations = request.POST.get('workshop_facilitations')
        panel_discussions = request.POST.get('panel_discussions')
        mentorship_programs_participated_in = request.POST.get('mentorship_programs_participated_in')
        online_courses_taught = request.POST.get('online_courses_taught')
        workshops_conducted = request.POST.get('workshops_conducted')
        volunteer_activities = request.POST.get('volunteer_activities')
        charitable_initiatives = request.POST.get('charitable_initiatives')
        community_leadership_roles = request.POST.get('community_leadership_roles')
        innovations_in_products = request.POST.get('innovations_in_products')
        new_inventions = request.POST.get('new_inventions')
        prototypes = request.POST.get('prototypes')
        startups_founded = request.POST.get('startups_founded')
        entrepreneurial_achievements = request.POST.get('entrepreneurial_achievements')
        business_ventures = request.POST.get('business_ventures')
        books_authored = request.POST.get('books_authored')
        published_research_papers = request.POST.get('published_research_papers')
        magazine_articles = request.POST.get('magazine_articles')
        artwork = request.POST.get('artwork')
        music_composition = request.POST.get('music_composition')
        writing = request.POST.get('writing')
        challenging_problem_solving_scenarios = request.POST.get('challenging_problem_solving_scenarios')
        complex_projects_overcome = request.POST.get('complex_projects_overcome')
        hackathons_won = request.POST.get('hackathons_won')
        competitions_or_challenges_won = request.POST.get('competitions_or_challenges_won')
        sports_achievements = request.POST.get('sports_achievements')
        leadership_roles = request.POST.get('leadership_roles')
        awards_in_non_professional_fields = request.POST.get('awards_in_non_professional_fields')
        industry_categories = request.POST.get('industry_categories')
        current_position=request.POST.get('current_position')
        intro = request.POST.get('intro')
        image = request.FILES.get('image')
        join_veriprofile_at = request.POST.get('join_veriprofile_at')
        profile_created_by = request.POST.get('profile_created_by')



        if date_of_birth:
                date_of_birth = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
        if graduation_dates:
                graduation_dates = datetime.strptime(graduation_dates, "%Y-%m-%d").date()
        if joining_date:
                joining_date = datetime.strptime(joining_date, "%Y-%m-%d").date()
        if joining_date1:
                joining_date1 = datetime.strptime(joining_date1, "%Y-%m-%d").date()
        if quit_date:
                quit_date = datetime.strptime(quit_date, "%Y-%m-%d").date()

        

        if email == '' or password == '':
            error(request, 'Email and password must be required')
            return redirect('add_user')
        if  first_name == '' or middle_name == '' or last_name == '' :
            error(request, 'Full name must be required')
            return redirect('add_user')
        if  mobile == '' :
            error(request, 'Mobile number must be required')
            return redirect('add_user')

        # Check if the email already exists in the database
        if Employee.objects.filter(email=email).exists():
            error(request, 'This email is already registered. Please use a different email.')
            return redirect('add_user')  # Redirect to the 'register' URL name or any other registration page
        
         # Check if the mobile already exists in the database
        if Employee.objects.filter(mobile=mobile).exists():
            error(request, 'This Contact Number is already exists. Please use a different number.')
            return redirect('add_user')  # Redirect to the 'register' URL name or any other registration page

        unique_id = uuid.uuid4().hex[:8]
        
        user = User.objects.create_user(email,email,password)
        user = User.objects.get(email=email)
        employee = Employee.objects.create(
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            gender=gender,
            marital_status=marital_status,
            date_of_birth=date_of_birth,
            nationality=nationality,
            religion=religion,
            preferred_language=preferred_language,
            languages_known=languages_known,
            wikipedia=wikipedia,
            personal_website=personal_website,
            time_zone=time_zone,
            email=email,
            password=password,
            facebook=facebook,
            ted=ted,
            youtube=youtube,
            linkedin=linkedin,
            degrees=degrees,
            institutions_attended=institutions_attended,
            gpa_academic_achivements=gpa_academic_achivements,
            graduation_dates=graduation_dates,
            job_title=job_title,
            company=company,
            industry=industry,
            joining_date=joining_date,
            job_location=job_location,
            job_title1=job_title1,
            joining_date1=joining_date1,
            quit_date=quit_date,
            company_name=company_name,
            industry_name=industry_name,
            location=location,
            role=role,
            responsibilities=responsibilities,
            certifications=certifications,
            licenses=licenses,
            awards=awards,
            publications=publications,
            researches=researches,
            projects=projects,
            portfolio=portfolio,
            # reasearch_link1=reasearch_link1,
            # reasearch_link2=reasearch_link2,
            # reasearch_link3=reasearch_link3,
            project_link1=project_link1,
            project_link2=project_link2,
            project_link3=project_link3,
            volunteer_work=volunteer_work,
            professional_memberships=professional_memberships,
            availability_for_networking=availability_for_networking,
            technical_skills=technical_skills,
            soft_skills=soft_skills,
            languages_spoken=languages_spoken,
            hobbies=hobbies,
            causes_and_interest=causes_and_interest,
            contact_information=contact_information,
            published_articles=published_articles,
            gitHub_repository_links=gitHub_repository_links,
            open_source_contributions=open_source_contributions,
            case_studies=case_studies,
            whitepapers=whitepapers,
            research_papers=research_papers,
            artifacts_or_creative_works=artifacts_or_creative_works,
            project_demonstrations_or_Videos=project_demonstrations_or_Videos,
            Patents_or_intellectual_property=Patents_or_intellectual_property,
            testimonials_or_recommendations=testimonials_or_recommendations,
            Open_Source_Projects=Open_Source_Projects,
            links_to_gitHub=links_to_gitHub,
            open_source_organizations_joined=open_source_organizations_joined,
            conference_talks=conference_talks,
            webinar_presentations=webinar_presentations,
            workshop_facilitations=workshop_facilitations,
            panel_discussions=panel_discussions,
            mentorship_programs_participated_in=mentorship_programs_participated_in,
            online_courses_taught=online_courses_taught,
            workshops_conducted=workshops_conducted,
            volunteer_activities=volunteer_activities,
            charitable_initiatives=charitable_initiatives,
            community_leadership_roles=community_leadership_roles,
            innovations_in_products=innovations_in_products,
            new_inventions=new_inventions,
            prototypes=prototypes,
            startups_founded=startups_founded,
            entrepreneurial_achievements=entrepreneurial_achievements,
            business_ventures=business_ventures,
            books_authored=books_authored,
            published_research_papers=published_research_papers,
            magazine_articles=magazine_articles,
            artwork=artwork,
            music_composition=music_composition,
            writing=writing,
            challenging_problem_solving_scenarios=challenging_problem_solving_scenarios,
            complex_projects_overcome=complex_projects_overcome,
            hackathons_won=hackathons_won,
            competitions_or_challenges_won=competitions_or_challenges_won,
            sports_achievements=sports_achievements,
            leadership_roles=leadership_roles,
            awards_in_non_professional_fields=awards_in_non_professional_fields,
            industry_categories=industry_categories,
            mobile=mobile,
            current_position=current_position,
            intro=intro,
            address=address,
            image=image,
            join_veriprofile_at=join_veriprofile_at,
            profile_created_by=profile_created_by,
            unique_id = unique_id,
            # aadhar_card=aadhar_card,
            # dr_licence=dr_licence,
            # pan_card=pan_card,
            )
        # messages.success(request,'Successfully Submit')
        employee.save()
        user.save()
        return redirect('view_profiles') 
    
    return render(request,'view_profiles.html',context)

@login_required(login_url='hr_login')
def view_profiles(request):
    hr_user = HRUser.objects.get(username=request.user.username)
    employee = Employee.objects.all().order_by("-id")
    hr = HRUser.objects.filter(hr_email=request.user.email)
    user = get_object_or_404(User, username=request.user.username)
    hr_user = get_object_or_404(HRUser, username=user)    

    hr_notifications = Notification.objects.filter(hr_users=hr_user).order_by('-id')
    unread_notifications = hr_notifications.filter(read_status=False)
    notification_count = unread_notifications.count()
    return render(request,'view_profiles.html',{'hr':hr ,'hr_user':hr_user,'employee':employee,'notification_count':notification_count,'hr_notifications':hr_notifications})

def insight(request):
    users = Employee.objects.all()
    company = Company.objects.all()
    hrs = HRUser.objects.all()
    hr = HRUser.objects.filter(hr_email=request.user.email)


    verified_users = Employee.objects.filter(status='Verified')
    non_verified_users = Employee.objects.exclude(status='Verified')

    user = get_object_or_404(User, username=request.user.username)
    hr_user = get_object_or_404(HRUser, username=user)    

    hr_notifications = Notification.objects.filter(hr_users=hr_user).order_by('-id')
    unread_notifications = hr_notifications.filter(read_status=False)
    notification_count = unread_notifications.count()

    return render(request,'insight.html',{'notification_count':notification_count, 'users':users,'hr_notifications':hr_notifications,'company':company,'hrs':hrs,'hr':hr,'verified_users':verified_users,'non_verified_users':non_verified_users})

def verification_center(request):
    hr = HRUser.objects.filter(hr_email=request.user.email)


    user = get_object_or_404(User, username=request.user.username)
    hr_user = get_object_or_404(HRUser, username=user)    

    hr_notifications = Notification.objects.filter(hr_users=hr_user).order_by('-id')
    unread_notifications = hr_notifications.filter(read_status=False)
    notification_count = unread_notifications.count()
    return render(request,'verification_center.html',{'hr':hr,'notification_count':notification_count,'hr_notifications':hr_notifications})

def assesment_center(request):
    hr = HRUser.objects.filter(hr_email=request.user.email)
    user = get_object_or_404(User, username=request.user.username)
    hr_user = get_object_or_404(HRUser, username=user)    

    hr_notifications = Notification.objects.filter(hr_users=hr_user).order_by('-id')
    unread_notifications = hr_notifications.filter(read_status=False)
    notification_count = unread_notifications.count()
    return render(request,'assesment_center.html',{'hr':hr,'notification_count':notification_count,'hr_notifications':hr_notifications})

def filtered_users(request):
    filter_criteria = request.POST.get('filter_criteria')
    filter_value = request.POST.get('filter_value')

    if filter_criteria:
        # Build the query dynamically based on the filter criteria
        users = User.objects.all()

        if filter_criteria == 'uid':
            users = users.filter(unique_id=filter_value)
        elif filter_criteria == 'name':
            users = users.filter(
                models.Q(first_name__icontains=filter_value) | models.Q(last_name__icontains=filter_value)
            )
        elif filter_criteria == 'registration_date':
            # Implement date filtering logic here
            pass
        # Add more filter criteria as needed

        return render(request, 'dashboard.html', {'users': users, 'filter_criteria': filter_criteria, 'filter_value': filter_value})

    return render(request, 'dashboard.html', {'users': User.objects.all()})

def hr_profile(request):
    return render(request, 'hr_profile.html')

def pdf(request):
    user = Employee.objects.filter(email=request.user.username)
    template_path = 'pdfreport.html'
    context = {'user': user}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="profile.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    # if error then show some funny view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

def user_gallery(request):
    user = Employee.objects.filter(email=request.user.username)
    if request.method == 'POST':
        images = request.FILES.getlist('images[]')
        users = get_object_or_404(User, username=request.user.username)
        employee = get_object_or_404(Employee, username=users)   
        for image in images:
            gallery = Gallery(image=image,user=employee)
            gallery.save()

        # Redirect to the same page after successful submission
        return redirect('userdashboard')

    images = Gallery.objects.all()
    
    return render(request, 'userdashboard.html', {'images': images})

def navbar(request):
    emp = Employee.objects.all()
    users = get_object_or_404(User, username=request.user.username)
    employee = get_object_or_404(Employee, username=users)  
    user_messages = Ping.objects.filter(user=employee).order_by('-id')
    unread_messages = user_messages.filter(read_status=False)
    message_count = unread_messages.count()  

    print(request.user)  # Add this line for debugging

    if request.method == 'POST':
        sender = get_object_or_404(User, username=request.user.username)
        emp = get_object_or_404(Employee, username=sender)

        message = request.POST.get('message')

        # Assuming you're getting user_messages as a QuerySet, you need to loop through it
        for user_message in user_messages:
            receiver = Employee.objects.get(email=user_message.sender.email)

            ping = Ping.objects.create(
                message=message,
                sender=emp,
                user=receiver,  # Associate the message with the specific user
            )
            ping.save()    


    # user_notifications = Notification.objects.filter(users=employee).order_by('-id')
    # unread_notifications = user_notifications.filter(read_status=False)
    # notification_count = unread_notifications.count()  


    return render(request, 'navbar.html', {'emp': emp,'message_count':message_count,'user_messages':user_messages,'employee':employee})

def temp_login(request):
    return render(request, 'temp_loginform.html')



# def setsession(request):
#     request.session['name'] = 'Raj'
#     # request.session['lname'] = 'Patil'
#     # request.session.set_expiry(10)
#     return render(request, 'setsession.html')

# def getsession(request):
#     # name = request.session['name']
#     name = request.session.get('name')
#     # lname = request.session.get('lname' , default='Patilso')
#     # age = request.session.setdefault('age','21')
#     # keys = request.session.keys()
#     # items = request.session.items()
#     return render(request, 'getsession.html',{'name':name})

# def delsession(request):
#     # if 'name' in request.session:
#     #     del request.session['name']
#     # if 'lname' in request.session:
#         # del request.session['lname']

#     request.session.flush()
#     request.session.clear_expired()
#     return render(request, 'delsession.html')


# def getsession(request):
#     name = request.session['name']
#     return render(request, 'getsession.html',{'name':name})


# def settestcookie(request):
#     request.session.set_test_cookie()
#     return render(request, 'set_test_cookie.html')

# def checktestcookie(request):
#     # print(request.session.test_cookie_worked())
#     return render(request, 'test_cookie_worked.html')

# def deltestcookie(request):
#     request.session.delete_test_cookie()
#     return render(request, 'del_test_cookie.html')


from asgiref.sync import async_to_sync
def test(request):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "usernotification_broadcast",
        {
            'type':'send_usernotification',
            'message':"UserNotification"
        }
    )
    return HttpResponse("Done")

    