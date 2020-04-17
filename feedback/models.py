from django.db import models

# Create your models here.

class College(models.Model):
    GENDER_CHOICE = (
        ('M','Male'),
        ('F','Female'),
    )

    system_no =models.IntegerField()
    gender = models.CharField(max_length=1,choices=GENDER_CHOICE)
    rating = models.TextField(max_length=65536,default="NaN")
    feedback = models.TextField(max_length=65536,default="NaN")

    def __str__(self):
        return str(self.system_no)