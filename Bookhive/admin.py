from django.contrib import admin

# Register your models here.

from .models import Books,Genre, Cart,Order
# Register your models here.

admin.site.register(Books)
admin.site.register(Genre)
admin.site.register(Cart)
admin.site.register(Order)



