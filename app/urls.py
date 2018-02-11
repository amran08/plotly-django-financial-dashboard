from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.views.generic import TemplateView
app_name = 'app'
urlpatterns = [
    path('', views.index, name='index'),
    path('add-company/', views.add_company, name='add-company'),
    path('<int:company_id>/company-info/', views.company_info, name='company-info'),
    path('<int:company_id>/company_cumulative_revenue/', views.company_cumulative_revenue, name='company-cumualtive-revenue'),
    path('<int:company_id>/company_cumulative_customer/', views.company_cumulative_customer, name='company-cumulative-customer'),
    path('<int:company_id>/company_observation_cohort/', views.company_observation_cohort, name='company-observation-cohort'),
    path('<int:company_id>/company_gross_mrr_churn/', views.company_gross_churn, name='company-gross-mrr-churn'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)