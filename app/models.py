from django.db import models
#from formatCheker import ContentTypeRestrictedFileField

class Company(models.Model):
    name = models.CharField(max_length=200)
    document = models.FileField(upload_to='documents/',null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class CompanyLog(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    date = models.DateField('date')
    month = models.IntegerField('month',default=0)
    day = models.IntegerField('day',default=0)
    year = models.IntegerField('year',default=0)
    customers= models.IntegerField('customers')
    revenue= models.FloatField('revenue')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

        