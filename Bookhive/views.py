from django.shortcuts import render, HttpResponse , redirect
from django.contrib.auth.models import User 
from django.contrib.auth import authenticate, login , logout
from django.contrib import messages
from .models import Books, Genre, Cart, Order

# Create your views here.

# def index(request):
#     return HttpResponse("Welcome To Book Hive!!!")

# def main(request):
#     return render(request, 'index.html', {})

def base(request):
    return render(request, 'base.html', {})


def home(request):
    books = Books.objects.filter(price__gt= 1000)
    print('books', books)
    return render(request, 'home.html', {'pop':books})

def featured(request):
    books = Books.objects.filter(status=True)
    return render(request, 'featured.html', {'books': books})

def download(request):
    return render(request, 'downloadapp.html', {})

def offers(request):
    offer_books = Books.objects.filter(offer_status= True)
    return render(request, 'offers.html', {'offer_books':offer_books})

def articles(request):
    return render(request, 'articles.html', {})



def auth(request):
    return render(request,'auth.html',{})

def authentic(request):
    return render(request,'authentic.html',{})

def register(request):
    if request.method == 'POST':
        username =  request.POST['email']
        password = request.POST['password']
        full_name = request.POST['full_name']

        first_name = full_name.split(' ')[0]
        last_name = full_name.split(' ')[1]

        if User.objects.filter(username=username).exists():
            messages.error(request, "User with this email already exists.")
            return render(request, 'auth.html',{})
        else : 
            users = User.objects.create_user(username=username, password=password, email=username, first_name=first_name, last_name=last_name)
            print("User created Successfully !!!", users)
            return redirect('/')
    
    
def signin (request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        # login 
        user = authenticate( request,username=email, password=password)
        if user is not None:
            login(request, user)
            print("User logged In", user)
            return redirect('/')
        else:
            print("Invalid Credentials!!")
            return redirect('/auth')
        
def sign_out(request):
    logout(request)
    return redirect('/')



# def popular(request, id=None):
#     if id:
#         books = Books.objects.get(id = id)  
#         print("books_genre_id", id)
#         print("books", books)# Filter books by genre
#     else:
#         books = Books.objects.all()  # Show all books if no genre is selected
#     return render(request, 'popular.html', {'books': books})

    
# def popular(request):
#     books = Books.objects.all()
#     genre = Genre.objects.all()
#     return render(request, 'popular.html', {'books': books , 'genre': genre} ) 

def popular(request, genre_id=None):
    books = Books.objects.filter(genre_id=genre_id) if genre_id else Books.objects.all()
    return render(request, 'popular.html', {
        'books': books,
        'genre': Genre.objects.all(),
        'genre_id': genre_id,
    })
    
def bk_details(request, genre=None, id=None) :
    if genre and id :
            book = Books.objects.get(genre=genre, id=id)  
            print("books_genre", genre)
            print("book", book)# Filter books by genre
    else:
        book = Books.objects.get(id=id)
    return render(request, 'book_details.html',{'book' : book})
    
    
# def cart(request) :
#     print("cart")
#     return render (request , 'cart.html', {})

def cart(request):
    if request.user.is_authenticated:
        try:
            # Attempt to get the user's existing cart
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            print('No cart found for the user')
            return redirect('/')  
        cart_items = cart.book.all()
        shipping_price=0
        grand_sum = 0
        for book in cart_items:
            if book.offer_status:
                grand_sum += (book.offer_price + book.shipping_cost)
            else:
                grand_sum +=( book.price + book.shipping_cost)
            shipping_price += book.shipping_cost
        cart.total = grand_sum
        print("cart total : ",cart.total)
        subtotal= grand_sum- shipping_price

        return render(request, 'cart.html', {"cart_items": cart_items, "grand_sum": grand_sum, "shipping_cost":shipping_price, "subtotal" : subtotal})
    else:
        print('User not logged in')
        return redirect('/auth') 



def add_to_cart(request, book_id):
    if request.user.is_authenticated:
        try:
            existing_cart = Cart.objects.get(user=request.user) #if user is existing in cart model i.e user has a cart
            if existing_cart:
                # add product to that cart
                existing_cart.book.add(book_id)
                print(f"Product {book_id} is added to the Cart!!")
        except Cart.DoesNotExist:
            # user does not have any cart yet
            # Create Cart
            new_cart = Cart.objects.create(user= request.user)
            # Add product to the cart
            new_cart.book.add(book_id)
            print(f"Product {book_id} is added to the Cart!!")
    else:
        print("User is not logged in")
    return redirect(request.META.get('HTTP_REFERER', '/'))


def delete_cart_item(request, book_id):
    print("book_id", book_id)
    cart = Cart.objects.get(user= request.user)
    cart.book.remove(book_id)
    print("Item deleted from Cart!")
    return redirect('/cart')


from uuid import uuid4
def checkout(request):
    cart = Cart.objects.get(user=request.user)
    cart_items = cart.book.all()
    
    # Calculate grand total properly
    grand_sum = sum(
        book.offer_price + book.shipping_cost if book.offer_status else book.price + book.shipping_cost
        for book in cart_items
    )

    print("checkout grandsum : ", grand_sum)
    
    if request.method == "POST":
        # Create a unique order_id
        order_id = str(uuid4())
        address = request.POST['address']
        mobile_no = request.POST['mobile_no']
        
        for book in cart_items:
            # Assign correct order amount per book
            order_amt = book.offer_price + book.shipping_cost if book.offer_status else book.price + book.shipping_cost
            
            Order.objects.create(
                order_id=order_id,
                user=request.user,
                product=book,
                address=address,
                mobile_no=mobile_no,
                order_amt=order_amt  # Save correct amount per book
            )
            # Remove ordered book from cart
            cart.book.remove(book)
        
        cart.total = 0  # Reset cart total
        
        print("Order Placed!!")
        return redirect('/')
    
    return render(request, 'checkout.html', {'cart_items': cart_items, 'grand_sum': grand_sum})



def orders(request):
    orders = Order.objects.filter(user=request.user).order_by('order_id')

    order_list = {}
    
    for order in orders:
        if order.order_id not in order_list:
            order_list[order.order_id] = {
                "order_id": order.order_id,
                "order_price": 0,  # Start from 0
                "status": order.status,
            }
        order_list[order.order_id]["order_price"] += order.order_amt  # Accumulate total price for that order_id

    # Convert dictionary to list
    order_list = list(order_list.values())

    print(order_list, orders)
    return render(request, "orders.html", {"order_list": order_list, "orders": orders})

