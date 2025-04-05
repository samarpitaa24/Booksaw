from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # path('', views.index , name= 'index'),
    
    # path('main', views.main , name='main'),
    
    path('base', views.home , name='base'),
    
    path('', views.home , name='home'),
    path('featured', views.featured , name='featured'),
    
    path('popular/', views.popular, name='popular'),
    path('popular/<int:genre_id>/', views.popular, name='popular-genre'),
    path('add-to-cart/<int:book_id>', views.add_to_cart, name='add-to-cart'),
    path('popular/<int:genre_id>/add-to-cart/<int:book_id>/', views.add_to_cart_with_genre, name='add-to-cart-with-genre'),
    # path('book_details/<int:book_id>/add-to-cart/<int:book_id>', views.add_to_cart, name='add-to-cart'),
    
    # book_details/2/add-to-cart/2
    
    
    path('offers', views.offers , name='offers'),
    path('download', views.download, name='download'),
    # path('articles', views.articles, name='articles'),
    
    path('cart', views.cart, name='cart'),
   


    path('basepopular/add-to-cart/<int:book_id>', views.add_to_cart, name='add-to-cart'),
    
     path('delete-cart-item/<int:book_id>', views.delete_cart_item, name='delete-cart-item'),

    path('checkout', views.checkout, name='checkout'),
    path('orders', views.orders, name='orders'),
    
    
    path('auth', views.auth, name='auth'),
    path('authentic', views.authentic, name='authentic'),
    
    path('register', views.register, name='register'),
    path('login', views.signin, name='login'),
    path('logout', views.sign_out, name='logout'),
    
     # path('basepopular/<str:genre>/book_details/<int:id>/', views.bk_details , name='book_details'),
    # basepopular/Adventure/book_details/21
    path('basepopular/book_details/<int:id>/', views.bk_details , name='book-details'),
    path('book_details/<int:id>/', views.bk_details , name='book-details'),
    
    path('add_book', views.add_book , name="add-product"),
    path("update_data/<int:id>",views.update_data, name="update-data"),
    path("delete_data/<int:id>",views.delete_data, name="deletedata"),
    
    #  path('chatbot/', views.chatbot_view, name='chatbot'),
     path('chatbot/', views.chatbot_view, name='chatbot'),
     path('clear-chat/', views.clear_chat, name='clear_chat'),

    
]
# http://127.0.0.1:8000/basepopular/Business/book_details/12
