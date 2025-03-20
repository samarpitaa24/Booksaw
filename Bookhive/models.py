from django.db import models
from django.contrib.auth.models import User
from datetime import datetime



# Create your models here.
class Genre (models.Model):
    genre_name = models.CharField(max_length=255)
            
    def __str__(self):
        return self.genre_name
    
class Books(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='books')
    author = models.CharField(max_length=100)
    price = models.IntegerField()
    # GENRE_LIST = [('Business', 'Business'), ('Romance','Romance'), ('Adventure','Adventure'), ('Fiction','Fiction'),('Mystery','Mystery')]
    # genre = models.CharField(max_length=255, choices= GENRE_LIST  , blank=True , null= True)
    genre = models.ForeignKey(Genre , related_name='genre', on_delete=models.CASCADE )
    desc = models.TextField()
    status = models.BooleanField(default=True)
    offer_status = models.BooleanField(default=False) 
    offer_price = models.IntegerField(default = 0)
    shipping_cost = models.IntegerField(default = 0)
    
    def __str__(self):
        return self.name
    
class Cart(models.Model):
    user = models.ForeignKey(User, related_name='customer', on_delete=models.CASCADE) #user id
    book = models.ManyToManyField(to= Books, related_name='cart_books', blank= True) #book id
    total = models.IntegerField(default=0)
    
    def __str__(self):
        return self.user.first_name
  
    
class Order(models.Model):
    order_id = models.CharField(max_length=50) # to identify order group
    user = models.ForeignKey(User, related_name='order_customer', on_delete=models.CASCADE)
    product = models.ForeignKey(Books, related_name='order_item', on_delete=models.CASCADE)
    address = models.CharField(max_length=200)
    mobile_no = models.CharField(max_length=10)
    date = models.DateTimeField(default=datetime.now())
    STATUS_CHOICES = [('Pending', 'Pending'), ('Delivered', 'Delivered'), ('On the Way', 'On the way')]
    status = models.CharField(max_length=50, choices= STATUS_CHOICES, default='pending')
    order_amt = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.product.name} - {self.user.first_name}'
    