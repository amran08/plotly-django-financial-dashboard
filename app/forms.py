from django import forms
from .models import Company,CompanyLog

class AddCompany(forms.ModelForm):
      name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Company Name'}))
      document = forms.FileField(widget=forms.FileInput(attrs={'class':'form-control','placeholder':'','accept':'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'}))
      class Meta:
        model = Company
        fields = ('name', 'document',)