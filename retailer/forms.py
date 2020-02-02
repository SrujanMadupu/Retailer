from django.forms import ModelForm
from .models import Retailer


class RetailerForm(ModelForm):
    class Meta:
        model = Retailer
        fields = '__all__'
