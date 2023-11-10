from datetime import datetime
from django.utils import timezone
from datetime import timedelta
from django.db import models
from django.db.models import Count  # Import Count from django.db.models
import uuid
import json
from customadmin.models import Level
# from image_cropping import ImageCropField, ImageRatioField
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_celery_beat.models import PeriodicTask,CrontabSchedule


class ProfileManager(models.Manager):
    def top_profiles(self, num_profiles=10):
        """
        Get the top profiles based on unique viewer counts.
        """
        profiles = self.annotate(viewer_count=Count('unique_visitors')).order_by('-viewer_count')[:num_profiles]
        
        # Debugging: Print the viewer_count for each profile
        for profile in profiles:
            print(f"Profile: {profile}, Viewer Count: {profile.viewer_count}")

        return profiles

def default_cover_image():
    return 'covers/Default Cover Image.png'  # Replace with the actual path to your default cover image

class Employee(models.Model):
    auth_token = models.CharField(max_length=100, null=True)
    is_verified_email = models.BooleanField(default=False)



    username = models.CharField(max_length=200, null=True)
    email = models.EmailField(max_length=100 , unique=True)
    password = models.CharField(max_length=100,null=True,blank=True)
    c_password = models.CharField(max_length=100,null=True,blank=True)
    unique_id = models.CharField(max_length=100, unique=True, null=True)
    first_name = models.CharField(max_length=100,null=True)
    last_name = models.CharField(max_length=100,null=True)
    location = models.CharField(max_length=200,null=True)
    contact = models.CharField(max_length=200,null=True)
    image = models.ImageField(upload_to="pics/",null=True)  

    update_status = models.BooleanField(default=False)
    
    salutation = models.CharField(max_length=100,null=True)
    middle_name = models.CharField(max_length=100,null=True)
    gender = models.CharField(max_length=100,null=True)
    date_of_birth = models.CharField(max_length=100,blank=True,null=True)
    marital_status = models.CharField(max_length=100,null=True)
    religion = models.CharField(max_length=100,null=True)
    nationality = models.CharField(max_length=100,null=True)
    native_language = models.CharField(max_length=100,null=True)
    languages_known = models.CharField(max_length=100,null=True)
    
    # address
    house_no = models.CharField(max_length=200,null=True)
    street = models.CharField(max_length=200,null=True)
    landmark = models.CharField(max_length=200,null=True)
    country = models.CharField(max_length=200,null=True)
    state = models.CharField(max_length=200,null=True)
    city = models.CharField(max_length=200,null=True)
    zip = models.CharField(max_length=200,null=True)

    # hometown
    home_country = models.CharField(max_length=200,null=True)
    home_state = models.CharField(max_length=200,null=True)
    home_city = models.CharField(max_length=200,null=True)
    home_village = models.CharField(max_length=200,null=True)
    home_zip = models.CharField(max_length=200,null=True)

    # Current Occupation:
    occupation_name = models.CharField(max_length=200,null=True,blank=True)
    
    business_company_name = models.CharField(max_length=200,null=True,blank=True)
    industry = models.CharField(max_length=100,blank=True,null=True)
    subcategory = models.CharField(max_length=100,blank=True,null=True)
    formation_type = models.CharField(max_length=100,blank=True,null=True)
    business_category = models.CharField(max_length=100,blank=True,null=True)
    business_start_date = models.CharField(max_length=100,blank=True,null=True)
    business_turnover = models.CharField(max_length=100,blank=True,null=True)
    business_country = models.CharField(max_length=100,blank=True,null=True)
    business_state = models.CharField(max_length=100,blank=True,null=True)
    business_city = models.CharField(max_length=100,blank=True,null=True)
    business_village = models.CharField(max_length=100,blank=True,null=True)
    business_zip = models.CharField(max_length=100,blank=True,null=True)

    def save(self, *args, **kwargs):
        # Check if the image field is empty (None)
        if not self.image:
            self.image = 'pics/default_profile.jpg'  # Set the default image path
            
        super().save(*args, **kwargs)





    unique_visitors = models.JSONField(default=list)

    objects = ProfileManager()

    # #verify 
    is_basic_details_verified = models.BooleanField(default=False)
    is_address_verified = models.BooleanField(default=False)
    is_qualification_verified = models.BooleanField(default=False)
    is_occupation_verified = models.BooleanField(default=False)
    is_experience_verified = models.BooleanField(default=False)
    is_honors_verified = models.BooleanField(default=False)
    is_skillsets_verified = models.BooleanField(default=False)
    is_proofofwork_verified = models.BooleanField(default=False)
    is_socialwork_verified = models.BooleanField(default=False)
    is_innovations_verified = models.BooleanField(default=False)
    is_program_attend_verified = models.BooleanField(default=False)
   
    status = models.CharField(max_length=200, default="Not-verified")
    time_zone = models.CharField(max_length=200, null=True)
    profile_created_by = models.CharField(max_length=200, null=True)
    cover_image = models.ImageField(upload_to='covers/', default=default_cover_image)
    join_veriprofile_at = models.DateField(auto_now_add=True, null=True)

class SocialLinks(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    name = models.CharField(max_length=300, null=True)
    link = models.URLField(null=True)

class Qualification(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    degree = models.CharField(max_length=300, null=True)
    specialization = models.CharField(max_length=500, null=True)
    passing_year = models.CharField(max_length=500, null=True)
    college = models.CharField(max_length=500, null=True)
    
class AdditionalQualification(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    name = models.CharField(max_length=300, null=True)
    details = models.CharField(max_length=300, null=True)

class Jobs(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE,null=True)
    job_title = models.CharField(max_length=200,null=True,blank=True)
    company_name = models.CharField(max_length=200,null=True,blank=True)
    joining_date = models.CharField(max_length=100,blank=True,null=True)
    upload_id =models.ImageField(upload_to='occupation/',blank=True,null=True)
    job_location = models.CharField(max_length=200,null=True,blank=True)
    job_industry = models.CharField(max_length=200,null=True,blank=True)

class Experience(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE,null=True)
    ex_job_title = models.CharField(max_length=200,null=True)   
    ex_company_name = models.CharField(max_length=200,null=True)   
    ex_joining_date = models.CharField(max_length=100,blank=True,null=True)
    ex_quit_date = models.CharField(max_length=100,blank=True,null=True)   
    ex_upload_id =models.ImageField(upload_to='experience/',blank=True,null=True)
    ex_job_location = models.CharField(max_length=200,null=True)  
    ex_job_industry = models.CharField(max_length=200,null=True)  

class Honors(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE,null=True)
    honors = models.CharField(max_length=100 ,null=True,blank=True)
    honor_type = models.CharField(max_length=100 ,null=True,blank=True)
    awards_name = models.CharField(max_length=100 ,null=True,blank=True)
    awards_given_by = models.CharField(max_length=100 ,null=True,blank=True)

class Note (models.Model):
    employee= models.CharField(max_length=100,null=True)
    note = models.CharField(max_length=300,null=True)
    date = models.DateField(auto_now_add=True, blank=True,null=True)

class Skills(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE,null=True)
    skill_name = models.CharField(max_length=100 ,null=True,blank=True)
    skill_filed = models.CharField(max_length=100 ,null=True,blank=True)   

class ProofOfWork(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE,null=True)
    proof_of_work = models.CharField(max_length=300,null=True)
    proof_of_work_input = models.CharField(max_length=300,null=True)

class MediaReferences(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE,null=True)
    name = models.CharField(max_length=200,null=True)
    link = models.URLField(null=True)

class SocialWork(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE,null=True)
    social_work = models.CharField(max_length=100,null=True)
    social_work_input = models.CharField(max_length=100,null=True)

class Innovation(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE,null=True)
    innovation_name = models.CharField(max_length=200,null=True)
    proof_of_concept = models.CharField(max_length=200,null=True)
    upload_info_video = models.ImageField(upload_to='innovationvid/',null=True)
    upload_info_image = models.ImageField(upload_to='innovationimg/',null=True)
    date_of_inovation = models.CharField(max_length=200,null=True)
    upload_info_certificate = models.ImageField(upload_to='innovationcer/',null=True)
    innovation_link = models.CharField(max_length=200,null=True)
    reference_name = models.CharField(max_length=200,null=True)
    reference_contact = models.CharField(max_length=200,null=True)

class OtherActivities(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE,null=True)
    act_type = models.CharField(max_length=200,null=True)
    act_title = models.CharField(max_length=200,null=True)
    act_link = models.URLField(null=True)
    act_date = models.CharField(max_length=200,null=True)
 
class Payment(models.Model):
    order_id = models.CharField(max_length=100,null=True,blank=True)
    payment_id = models.CharField(max_length=100,null=True,blank=True)
    # user_course = models.ForeignKey(UserCourse,on_delete=models.CASCADE,null=True)
    user = models.ForeignKey(Employee,on_delete=models.CASCADE,null=True)
    level = models.ForeignKey(Level,on_delete=models.CASCADE,null=True)
    date = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False)

class UserLevel(models.Model):
    user= models.ForeignKey(Employee, on_delete=models.CASCADE,null=True)
    level = models.ForeignKey(Level, on_delete=models.CASCADE,null=True,default="Smart")

class Company(models.Model):
    # 1.	Organization Details:
    name_of_partner = models.CharField(max_length=200, null=True)
    phone = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True)
    address = models.CharField(max_length=200, null=True)
    industry_field = models.CharField(max_length=200, null=True)

    # 2.	Partnership Information:
    nature_of_partenership = models.CharField(max_length=200, null=True)
    duration_of_partenership = models.CharField(max_length=200, null=True)

    # 3.	Verification Requirements:
    # types_of_verificaton_needed = models.CharField(max_length=300, null=True)
    select_by_requirements = models.CharField(max_length=300, null=True)
    select_by_level = models.CharField(max_length=300, null=True)
    number_of_candidates = models.CharField(max_length=300, null=True)

    # 4.	Integration and Technical Details (if applicable):
    technical_point_of_contact = models.CharField(max_length=300, null=True)
    do_you_need_api = models.CharField(max_length=300, null=True)

    data_retention_policy = models.CharField(max_length=200, null=True)

    # 5.	Data Handling and Privacy:
    data_sharing = models.ImageField(upload_to="imgs/" , default="profile1.jpg", null=True)


    # 6.	Terms and Conditions: (T&C shown and below checkbox)

    responsibilities = models.BooleanField(default=False , null=True)
    partnership_agreement = models.BooleanField(default=False , null=True)


    # 7.	Additional
    requests_for_requirements = models.CharField(max_length=1000, null=True)
    additional_doc = models.CharField(max_length=1000, null=True)
    is_approved = models.BooleanField(default=False)

class HRUser(models.Model):
    # •	Data Protection Measures
    # 1.	Register Your HR
    company_name = models.ForeignKey(Company, null=True,on_delete=models.CASCADE) 
    first_name = models.CharField(max_length=200, null=True)
    last_name = models.CharField(max_length=200, null=True)
    address_hr = models.CharField(max_length=200, null=True)
    designation_in_company = models.CharField(max_length=200, null=True)
    contact = models.CharField(max_length=200, null=True)
    hr_email = models.CharField(max_length=200, null=True)
    username = models.CharField(max_length=200, null=True)
    password = models.CharField(max_length=200, null=True)
    employment_number = models.CharField(max_length=200, null=True)
    employment_id = models.ImageField(upload_to="imgs/" , default="profile1.jpg", null=True)
    aadhar_card = models.ImageField(upload_to="imgs/" , default="profile1.jpg", null=True) 
    is_approved = models.BooleanField(default=False)

class MediaReference(models.Model):
    reference_link = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True , null=True)
    updated_at = models.DateTimeField(auto_now=True , null=True)

class Category(models.Model):
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    user = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)

class Photo(models.Model):
    class Meta:
        verbose_name = 'Photo'
        verbose_name_plural = 'Photos'
    
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(null=False, blank=False)
    description = models.TextField(null=True,blank=True)

class LoginHistory(models.Model):
    user = models.ForeignKey(Employee, on_delete=models.CASCADE)
    logout_time = models.DateTimeField(default=timezone.now)

class AdminNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def mark_as_read(self):
        self.is_read = True
        self.save()

    def __str__(self):
        return f"Admin Notification for {self.user.username}: {self.message}"
    
class Notification(models.Model):
    message = models.TextField(null=True)
    broadcast_on = models.DateTimeField(null=True)
    sent = models.BooleanField(default=False)

    class Meta:
        ordering = ['-broadcast_on']

@receiver(post_save, sender=Notification)
def notification_handler(sender, instance, created, **kwargs):
    # call group_send function directly to send notificatoions or you can create a dynamic task in celery beat
    if created:
        schedule, created = CrontabSchedule.objects.get_or_create(hour = instance.broadcast_on.hour, minute = instance.broadcast_on.minute, day_of_month = instance.broadcast_on.day, month_of_year = instance.broadcast_on.month)
        task = PeriodicTask.objects.create(crontab=schedule, name="broadcast-notification-"+str(instance.id), task="notifications_app.tasks.broadcast_notification", args=json.dumps((instance.id,)))

    #if not created:

class Ping(models.Model):
    sender = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='sent_pings' ,null=True)
    user = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True)
    message = models.CharField(max_length=400)
    read_status = models.BooleanField(default=False)



    created_at = models.DateTimeField(auto_now_add=True,null=True)

    def time_elapsed(self):
        now = timezone.now()
        elapsed_time = now - self.created_at

        if elapsed_time < timedelta(minutes=1):
            return f'{elapsed_time.seconds} sec ago'
        elif elapsed_time < timedelta(hours=1):
            minutes = elapsed_time.seconds // 60
            return f'{minutes} min ago'
        elif elapsed_time < timedelta(days=1):
            hours = elapsed_time.seconds // 3600
            return f'{hours} hr ago'
        else:
            days = elapsed_time.days
            return f'{days} days ago'

class Gallery(models.Model):
    user = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True)
    image = models.ImageField(upload_to='gallery/')
    date = models.DateField(auto_now_add=True,null=True)

