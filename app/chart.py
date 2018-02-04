from .models import Company,CompanyLog
from datetime import datetime
from django.db import connection
from django.http import JsonResponse

def get_cumulative_revenue_by_month_year(company_id):
    cursor = connection.cursor()
    cursor.execute("select app_companylog.year,app_companylog.month,sum(revenue) from app_companylog WHERE company_id="+str(company_id)+" GROUP BY year,month ORDER BY year,month")
    data = []
    for p in cursor.fetchall():
        data.append({
                     'year':p[0],
                     'month':p[1],
                     'cum_revenue':p[2]
                    })
    json = JsonResponse(data,safe=False)  
    return json

def get_cumulative_customer_by_month_year(company_id):
    cursor = connection.cursor()
    cursor.execute("select app_companylog.year,app_companylog.month,count(customers) from app_companylog WHERE company_id="+str(company_id)+"AND revenue>0 GROUP BY year,month ORDER BY year,month")
    data = []
    for p in cursor.fetchall():
        data.append({
                     'year':p[0],
                     'month':p[1],
                     'cum_customers': p[2]
                    })
    json = JsonResponse(data,safe=False)  
    return json
