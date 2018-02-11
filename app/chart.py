from .models import Company,CompanyLog
from datetime import datetime
from django.db import connection
from django.http import JsonResponse

def get_cumulative_revenue_by_month_year(company_id):
    cursor = connection.cursor()
    cursor.execute("select app_companylog.year,app_companylog.month,sum(revenue),app_companylog.date from app_companylog WHERE company_id="+str(company_id)+" GROUP BY year,month,date ORDER BY year,month,date")
    data = []
    for p in cursor.fetchall():
        data.append({
                     'year':p[0],
                     'month':p[1],
                     'cum_revenue':p[2],
                     'date':p[3]
                    })
    json = JsonResponse(data,safe=False)  
    return json

def get_cumulative_customer_by_month_year(company_id):
    cursor = connection.cursor()
    cursor.execute("select app_companylog.year,app_companylog.month,count(customers),app_companylog.date from app_companylog WHERE company_id="+str(company_id)+"AND revenue>0 GROUP BY year,month,date ORDER BY year,month,date")
    data = []
    for p in cursor.fetchall():
        data.append({
                     'year':p[0],
                     'month':p[1],
                     'cum_customers': p[2],
                     'date':p[3]
                    })
    json = JsonResponse(data,safe=False)  
    return json

def observation_cohort(company_id):
    cursor = connection.cursor()
    cursor2 = connection.cursor()
    result = []
    query = """SELECT array_agg(final_result.customers),
                final_result.min_date
                from 
                (SELECT MIN(date) as min_date,customers
                from app_companylog
                WHERE revenue > 0
                AND company_id="""+str(company_id)+"""
                AND customers in
                    (SELECT customers from app_companylog 
                    GROUP BY customers 
                    ORDER BY customers)
                GROUP BY customers
                ORDER BY customers
                ) as final_result 
                GROUP BY final_result.min_date
                Order BY final_result.min_date"""
    cursor.execute(query)            
    for p in cursor.fetchall():
        query_2 = """SELECT sum(revenue), date
                    FROM app_companylog
                    where customers IN
                    ("""+','.join(str(x) for x in p[0])+""")
                    AND date >= '"""+ str(p[1]) + """'::date
                    GROUP BY date
                    ORDER BY date"""

        cursor2.execute(query_2)

        # for p2 in cursor2.fetchall():
        #     result.append({
        #         'info':p2,
        #         'cohort_date':str(p[1]),
        #         })

        result.append({
            'info': cursor2.fetchall(),
            'cohort_date': str(p[1]),
            'month':str(p[1].strftime("%m")),
            'year':str(p[1].strftime("%Y"))
            });
    
    # print(result)

    return JsonResponse(result,safe=False)     

def get_previous_month(month,year):
    MAX_MONTH =12
    MIN_MONTH =1
    if(month==MIN_MONTH):
        month=MAX_MONTH
        year=year-1
    else:
        month = month-1
    return [month,year]         

def get_revenue_sum(company_id, customers, month, year):
    query = """SELECT SUM(revenue), month, year
                FROM app_companylog
                WHERE
                month="""+str(month)+""" AND year="""+str(year)+""" AND
                customers in ("""+",".join(str(x) for x in customers)+""")
                AND company_id="""+str(company_id)+"""
                GROUP BY month, year"""
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall();
    return result[0][0]

def get_upsell_downsell(company_id, customers, current_month, current_year):
    prev_month, prev_year = get_previous_month(current_month, current_year)
    cursor = connection.cursor();
    query = """SELECT sum(revenue) as revenue 
				FROM app_companylog 
				WHERE month="""+str(prev_month)+""" AND 
                company_id = """+str(company_id)+""" AND
				year="""+str(prev_year)+""" AND 
				customers in ("""+','.join(str(x) for x in customers)+""") 

          UNION ALL 
         
				SELECT sum(revenue)  as revenue
				FROM app_companylog 
				WHERE month="""+str(current_month)+""" AND 
                company_id="""+str(company_id)+""" AND
				year="""+str(current_year)+""" AND 
				customers in ("""+','.join(str(x) for x in customers)+""")"""
    cursor.execute(query)
    result = cursor.fetchall()
#    print("Upsell and downsell For : " + str(current_month) + " : " + str(current_year))
   #print(result)
    return result[1][0] - result[0][0]

def get_gross_mrr_churn(company_id):
    
    cursor = connection.cursor()

    query = """SELECT SUM(revenue), month, year
            FROM app_companylog
            WHERE company_id="""+str(company_id)+"""
            GROUP BY year, month
            ORDER BY year,month"""
    cursor.execute(query)
    total_revenue = cursor.fetchall()

    query = """SELECT array_agg(DISTINCT customers), month, year
                FROM app_companylog
                WHERE revenue=0
                AND company_id="""+str(company_id)+"""
                GROUP BY month, year
                ORDER BY year, month"""
    cursor.execute(query);
    all_results = cursor.fetchall()
    data = [{
        "percentage" : 0,
        "month" : all_results[0][1],
        "year" : all_results[0][2]
    }]
    churned_revenue_by_date = {}
    for i  in range(1, len(all_results)):
        prev_result = all_results[i-1]
        result = all_results[i]
        
        total_revenue_in_previous_month = total_revenue[i-1][0]
        current_month_no_revenue_customers = set(result[0])
        previous_month_no_revenue_customers = set(prev_result[0])
        churn_customers = list(current_month_no_revenue_customers - previous_month_no_revenue_customers);
        percentage = 0
        month = result[1]
        year = result[2]
        
        if(len(churn_customers) > 0):
            # there was some churn customers
            previous_month, previous_year = get_previous_month(month, year)
            churned_revenue = get_revenue_sum(company_id, churn_customers, previous_month, previous_year)
            #print("Churned REvenue : " + str(churned_revenue))
            #print("Total Revenue : " + str(total_revenue_in_previous_month))
            churned_revenue_by_date[str(month)+"-"+str(year)] = churned_revenue
            percentage = -(churned_revenue / total_revenue_in_previous_month) * 100
        else:
            # no churn customer
            percentage = 0
            churned_revenue_by_date[str(month)+"-"+str(year)] = 0
        
        data.append({
            "percentage" : percentage,
            "month" : month,
            "year" : year
        })

    print("Churn revenue by date")
    print(churned_revenue_by_date)
     ## determining upselling and downselling 
    query3 = """ 
            SELECT 
            month,year,array_agg(DISTINCT customers)
            FROM app_companylog
            WHERE revenue >0
            AND company_id="""+str(company_id)+"""
            GROUP BY month,year
            ORDER BY year,month"""
    cursor.execute(query3)
    result_query3 = cursor.fetchall()
    #print("Printing possible common users")
    data2 = [{
        'month' : result_query3[0][0],
        'year' : result_query3[0][1],
        'upsell_downsell' : 0
    }]

    for i  in range(1, len(result_query3)):
        current_month = result_query3[i][0]
        current_year = result_query3[i][1]
        total_revenue_in_previous_month = total_revenue[i-1][0]
        previous_months_customers = set(result_query3[i-1][2])
        current_months_customers = set(result_query3[i][2])
        upsell_downsell_customers = list(previous_months_customers & current_months_customers)

        upsell_downsell = get_upsell_downsell(company_id, 
                                            upsell_downsell_customers,
                                                current_month,
                                                current_year)
            # adding churned revenue
        upsell_downsell -= churned_revenue_by_date[str(current_month)+"-"+str(current_year)]

        data2.append({
                'month' : current_month,
                'year' : current_year,
                'upsell_downsell' : (upsell_downsell / total_revenue_in_previous_month) * 100
        })

   #data2 for upsell/downsell set 
    result = [
        data,data2
    ]

    return JsonResponse(result, safe=False)

