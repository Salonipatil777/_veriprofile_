from django.db import models


# Create your models here.
class Level(models.Model):
    image = models.FileField(upload_to="images/",null=True)   
    name = models.CharField(max_length=200,default="Smart")
    price = models.IntegerField(null=True)

class DailyInspiration(models.Model):
    image = models.ImageField(upload_to='daily_inspirations/')
    date = models.DateField(auto_now_add=True,null=True)


