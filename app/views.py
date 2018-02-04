import csv 
import codecs
from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from django.template import loader
from .models import Company,CompanyLog
from django.http import Http404
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from .forms import AddCompany
from django.db import transaction
from datetime import datetime
from . import chart
from django.views.generic import TemplateView

def index(request):
    company_list = Company.objects.order_by('-created_at')[:100]
    template = loader.get_template('app/index.html')
    context = {
        'form':AddCompany(),
        'company_list': company_list,
    }
    return render(request, 'app/index.html', context)

@transaction.atomic
def add_company(request):
    # If this is a POST request then process the Form data
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request (binding):
        form = AddCompany(request.POST, request.FILES)
        # Check if the form is valid:
        if form.is_valid():
            try:
                #with transaction.atomic():
                file = request.FILES["document"]
                company_instance = form.save()
                reader = csv.DictReader(decode_utf8(file))  
                for row in reader:
                    company_log_instance = CompanyLog()
                    company_log_instance.company_id = company_instance.id
                    company_log_instance.customers =(row['Customer'])
                    company_log_instance.date =datetime.strptime(row['Date'], "%m/%d/%Y").strftime('%Y-%m-%d')
                    company_log_instance.day =datetime.strptime(row['Date'], "%m/%d/%Y").strftime('%d')
                    company_log_instance.month =datetime.strptime(row['Date'], "%m/%d/%Y").strftime('%m')
                    company_log_instance.year =datetime.strptime(row['Date'], "%m/%d/%Y").strftime('%Y')
                    company_log_instance.revenue =(row['Revenue'])  
                    company_log_instance.save()
                    
                # redirect to a new URL:
                messages.success(request, 'File Uploaded! ')
            except:
                company_instance.delete()
                messages.error(request, 'File Uploading failed,Only CSV uploadable')
            return HttpResponseRedirect(reverse('app:index', args=''))
        else:
            company_list = Company.objects.order_by('-created_at')[:100]
            content = {'form':form,'company_list':company_list}
            return render(request, 'app/index.html', content)
        
    # If this is a GET (or any other method) create the default form.
    else:
        return HttpResponseRedirect(reverse('app:index', args=''))

def decode_utf8(input_iterator):
    for l in input_iterator:
        yield l.decode('utf-8')

def company_info(request,company_id):
    context = {
        'company_id':company_id
    }
    return render(request, 'app/info.html',context)


## AJAX REQUESTS 


def company_cumulative_revenue(request,company_id):
    context = chart.get_cumulative_revenue_by_month_year(company_id)
    return context


def company_cumulative_customer(request,company_id):
     data = chart.get_cumulative_customer_by_month_year(company_id)
     return data


