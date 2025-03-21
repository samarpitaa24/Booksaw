from django import forms 
from .models import Books

class BookForm(forms.ModelForm):
    class Meta :
        model = Books 
        fields = ["name", "image","author","price","genre","desc","status","offer_status","offer_price","shipping_cost"]
        

    


