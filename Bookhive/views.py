from django.shortcuts import render, HttpResponse , redirect,HttpResponseRedirect
from django.contrib.auth.models import User 
from django.contrib.auth import authenticate, login , logout
from django.contrib import messages
from .models import Books, Genre, Cart, Order
from .forms import BookForm


from .data.books_data import books_data
from .data.authors_data import authors_data

from collections import Counter
from django.db.models import Count
from thefuzz import process
from django.urls import reverse

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

# def articles(request):
#     return render(request, 'articles.html', {})



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

def add_to_cart_with_genre(request, genre_id, book_id):
    return add_to_cart(request, book_id)



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
          
#  path('add_book', views.add_book , name="add-product"),
#     path("update_data/<int:id>",views.update_data, name="update-data"),
#     path("delete_data/<int:id>",views.delete_data, name="deletedata"),
    
    
def add_book(request):
    if request.method == "POST":
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("/")
        data = Books.objects.all()
    else:
        form = BookForm()
        data = Books.objects.all()
    return render(request, 'add_book.html', {'data':data, 'form' : form})

def update_data(request,id):
    if request.method == "POST":
        pi = Books.objects.get(pk=id)
        fm = BookForm(request.POST, instance=pi)
        if fm.is_valid():
            fm.save()
            return redirect("/")
    else :
        pi= Books.objects.get(pk=id)
        fm =BookForm(instance=pi)
    return render(request, 'update.html', {'form':fm})
    
    
def delete_data(request,id):
    if request.method=="POST":
        pi = Books.objects.get(pk=id)
        pi.delete()
        return HttpResponseRedirect("/") #redirects on homepage
    
    
#chatbot working 

# ## Function to generate clickable book link (if required later)
# def generate_book_link(book):
#     """Generate a clickable book title that links to the book's detail page."""
#     book_url = reverse('book-details', args=[book.id])
#     return f'<a href="{book_url}" target="_blank">{book.name}</a>'


# # Function to fetch trending books based on order history
# def get_trending_books(limit=5):
#     """Returns a list of trending books."""
#     trending_books = Books.objects.annotate(order_count=Count('order'))
#     trending_books = trending_books.order_by('-order_count')[:limit]  # Order by highest order count
#     return [book.name for book in trending_books]


# # Function to recommend books by genre
# def recommend_books_by_genre(genre):
#     """Recommends books based on the specified genre."""
#     allowed_genres = {"Fiction", "Adventure", "Romance", "Mystery", "Business"}

#     if genre.lower() not in {g.lower() for g in allowed_genres}:  
#         return "Sorry, we don't have books for that genre."

#     books = Books.objects.filter(genre__genre_name__iexact=genre)  # Case-insensitive search
#     recommendations = [book.name for book in books]

#     return f"Here are some {genre} books: {', '.join(recommendations)}" if recommendations else f"No books found in {genre} genre."


# # Function to recommend books by author
# def recommend_books_by_author(author):
#     """Recommends books based on the author."""
#     books_by_author = Books.objects.filter(author=author)
#     recommendations = [book.name for book in books_by_author]

#     return f"Books by {author}: {', '.join(recommendations)}" if recommendations else f"No books found by {author}."


# def get_book_info(book_title):
#     """Fetch book details from the books_data."""
#     for book in books_data:  # books_data is a list of dictionaries with book information
#         if book["title"].lower() == book_title.lower():
#             return f"'{book['title']}' by {book['author']}. {book['description']}"
    
#     return "Sorry, I couldn't find that book."


# # Fetch author details and notable works from authors_data
# def get_author_info(author_name):
#     """Fetch author details and notable works from authors_data."""
#     author_info = authors_data.get(author_name)

#     if author_info:
#         notable_works = ', '.join(author_info.get('notable_works', []))
#         suggestions = ', '.join(author_info.get('suggestions', []))
#         return f"{author_name}: {author_info['bio']} Notable works: {notable_works}. Suggested books: {suggestions}."
    
#     return "Sorry, I couldn't find that author."

# # Utility function to normalize author name (remove spaces and periods)
# def normalize_author_name(author_name):
#     """Normalize author name by removing spaces and periods."""
#     return author_name.replace(" ", "").replace(".", "").lower()


# def normalize_book_title(book_title):
#     """Normalize book title by removing spaces and periods and making it lowercase."""
#     return book_title.replace(" ", "").replace(".", "").lower()

# # Handle different types of user queries
# def get_bot_response(user_message):
#     """Handles different types of user queries using grouped keywords."""
#     user_message = user_message.lower().strip()
#     print(f"User Message: {user_message}")  # Debugging

#     # Define keyword sets
#     recommend_keywords = {
#         "recommend", "suggest", "advise", "give me", "recommendation",
#         "any good", "what should i read", "book for me", "suggestion"
#     }

#     genre_keywords = {
#         "mystery", "fantasy", "romance", "thriller", "science fiction",
#         "horror", "comedy", "drama", "historical", "adventure", "self-help",
#         "biography", "non-fiction", "dystopian", "classic", "crime",
#         "psychological", "business", "fiction"  # Added missing genres
#     }

#     author_keywords = {
#         "author", "writer", "who wrote", "who is", "written by", "creator of",
#         "who's the author", "who's the writer"
#     }

#     book_info_keywords = {
#         "book info", "tell me about", "describe", "book", "summary of",
#         "what is", "explain", "plot of", "story of", "what's this book about"
#     }

#     trending_keywords = {
#         "trending", "popular", "bestseller", "hot books", "top books",
#         "most read", "famous books", "best books", "top rated", "currently trending", "trending book"
#     }

#     irrelevant_phrases = [
#         "book info", "tell me about", "describe", "summary of", "what is", "explain", "plot of", "story of", "what's this book about"
#     ]
    
    
#     words = set(user_message.split())  # Convert user message to a set of words
#     print(f"Detected Words: {words}")  # Debugging

#     # If user asks for recommendations
#     if words & recommend_keywords:
#         genre = next((word for word in words if word in genre_keywords), None)
#         if genre:
#             print(f"Genre Extracted: {genre}")  # Debugging
#             return recommend_books_by_genre(genre)
#         return "Would you like a recommendation based on a genre or an author? Please specify!"

#     # If user just says "genre"
#     if user_message == "genre":
#         return "Which genre are you interested in? Please type the genre name (e.g., mystery, fantasy)."

#     # If user types a genre directly (e.g., "mystery")
#     if user_message in genre_keywords:
#         print(f"User specified genre: {user_message}")  # Debugging
#         return recommend_books_by_genre(user_message)

#     # If user just says "author"
#     if user_message == "author":
#         return "Which author are you asking about? Please type the author's name."

#     # Check if the user input matches an author name directly
#     normalized_user_message = normalize_author_name(user_message)  # Normalize user message
#     for author_name in authors_data.keys():
#         if normalized_user_message == normalize_author_name(author_name):
#             return get_author_info(author_name)  # Call function if a valid author is detected

#     # If user asks about an author
#     if words & author_keywords:
#         author_name = user_message.replace("who wrote", "").replace("who is", "").replace("written by", "").replace(
#             "author", "").replace("writer", "").replace("creator of", "").replace("who's the author", "").replace(
#             "who's the writer", "").strip()
#         print(f"Author Name Extracted: {author_name}")  # Debugging
#         return get_author_info(author_name) if author_name else "Which author are you asking about?"

#    # Check if the message contains book info keywords
#     if any(keyword in user_message for keyword in book_info_keywords):
#         # Remove irrelevant phrases while keeping the book title intact
#         book_title = user_message
#         for phrase in irrelevant_phrases:
#             book_title = book_title.replace(phrase, "").strip()

#         print(f"Extracted Book Title: {book_title}")  # Debugging

#         # Normalize the extracted book title
#         normalized_book_title = normalize_book_title(book_title)

#         print(f"Normalized Book Title: {normalized_book_title}")  # Debugging

#         # Call the get_book_info function with the normalized title
#         return get_book_info(normalized_book_title)


#     # If user asks about trending books
#     if words & trending_keywords:
#         print("Fetching Trending Books...")  # Debugging
#         trending_books = get_trending_books()
#         return f"Here are some trending books: {', '.join(trending_books)}" if trending_books else "No trending books found."

#     # Default response if no match is found
#     print("No match found.")  # Debugging
#     return "Sorry, I didn't understand that. Try asking for book recommendations, author info, or trending books!"



# chat_history = []

# def chatbot_view(request):
#     """
#     Handles the chatbot interaction where the user submits messages and receives bot responses.
#     """
#     global chat_history

#     if request.method == "POST":
#         # Get the user's message
#         user_message = request.POST.get("user_message", "").strip()

#         if user_message:
#             # Add the user's message to the chat history
#             chat_history.append({"text": user_message, "user": True})

#             # Get the bot's response based on the user message
#             bot_response = get_bot_response(user_message)

#             # Add the bot's response to the chat history
#             chat_history.append({"text": bot_response, "user": False})

#     return render(request, 'chatbot.html', {
#         'chat_history': chat_history
#     })







# Importing the keywords from the external data file , for random 
from .data.keywords import recommendation_keywords

# def handle_book_recommendation_request(user_message):
#     # Split the user message into words/phrases
#     user_words = user_message.lower().split()  # Split based on space; can enhance with regex for more complex splitting

#     # Check if any word or phrase matches with keywords
#     for word in user_words:
#         if word in recommendation_keywords:
#             # If the message contains a recommendation request, ask for genre
#             return "Please specify a genre. Available genres are: Fiction, Adventure, Romance, Mystery, Business."

#     # If no match is found, return a fallback message
#     return "Sorry, I didn't quite understand your request. Could you please ask for a book recommendation?"


#for genre based 
from .data.keywords import genre_keywords

def match_genre(user_message):
    """
    Match user input with genre keywords and return the matched genre(s).
    """
    matched_genres = []
    
    # Iterate over all genres and check if the user message contains any of the genre-specific keywords
    for genre, keywords in genre_keywords.items():
        for keyword in keywords:
            if keyword.lower() in user_message.lower():
                if genre not in matched_genres:
                    matched_genres.append(genre)
                    
    return matched_genres

def recommend_books_by_genre(user_message):
    """
    Recommend books based on the genre(s) specified in the user message.
    """
    # Step 1: Match genre from user message
    matched_genres = match_genre(user_message)
    
    if not matched_genres:
        return "Sorry, I couldn't identify the genre. Could you specify a genre like Fiction, Romance, etc.?"
    
    # Step 2: Retrieve books based on matched genres
    books_to_display = []
    
    if len(matched_genres) == 1:
        # For a single genre, display 3 books from that genre
        genre = matched_genres[0]
        books = Books.objects.filter(genre__genre_name=genre)[:3]
        books_to_display = books
    elif len(matched_genres) > 1:
        # For combined genres, display 2 books from each genre
        for genre in matched_genres:
            books = Books.objects.filter(genre__genre_name=genre)[:2]
            books_to_display.extend(books)
    
    # Step 3: Format the response with book details
    response = "Here are some books based on your preferences:\n"
    for book in books_to_display:
        response += f"{book.name} by {book.author} - Price: {book.price} Rs\n"
    
    return response




def extract_authors_from_message(user_message):
    """
    Extracts author names from the user message. Supports multiple authors separated by commas or conjunctions.
    """
    author_keywords = ['and', 'or']
    message_parts = user_message.lower().split(',')
    
    authors = []
    for part in message_parts:
        part = part.strip()
        # Try to match each part with the known authors in authors_data
        for author in authors_data.keys():
            if author.lower() in part:  # If part of the message matches an author
                authors.append(author)
    
    return authors

def recommend_books_by_author(user_message):
    """
    Recommends books based on the author names specified by the user.
    Extracts authors from the message, checks them in authors_data, and returns suggestions.
    """
    # Step 1: Extract author names from the message
    authors = extract_authors_from_message(user_message)

    if not authors:
        return "Sorry, I couldn't recognize any authors in your message. Could you please mention the author's name?"

    # Step 2: Check for valid authors in the authors_data
    recommendations = {}
    
    for author in authors:
        if author in authors_data:
            recommendations[author] = {
                "bio": authors_data[author]["bio"],
                "notable_works": authors_data[author]["notable_works"],
                "suggestions": authors_data[author]["suggestions"][:2]  # Only show 2 book suggestions
        }
        else:
            recommendations[author] = "Sorry, I couldn't find any information for this author."

    # Step 3: Format the response to display the suggestions
    response = ""
    for author, data in recommendations.items():
        if isinstance(data, dict):
            response += f"**{author}**: {data['bio']}\n"
            response += f"Notable Works: {', '.join(data['notable_works'])}\n"
            response += f"Suggested Books: {', '.join(data['suggestions'])}\n\n"
        else:
            response += f"{data}\n\n"

    return response


def handle_book_recommendation_request(user_message):
    """
    Handle book recommendation request based on the user's message.
    - Case 1: User asks for book recommendation without specifying genre/author.
    - Case 2: User asks for book recommendation with genre specified.
    - Case 3: User asks for book recommendation with author specified.
    - Case 4: User specifies only genre.
    """
    
    # Check if the user message contains any of the recommendation keywords like 'suggest', 'recommend', etc.
    recommendation_keywords_list = recommendation_keywords["recommendation"]
    user_message_lower = user_message.lower()

    # Case 1: If user asks for a recommendation with genre or author specified (via keywords)
    if any(keyword in user_message_lower for keyword in recommendation_keywords_list):
        # Check if user has specified a genre
        matched_genres = match_genre(user_message)
        if matched_genres:
            # Case 2: Genre specified, call recommend_books_by_genre
            return recommend_books_by_genre(user_message)
        
        # Case 3: If the message mentions author names (without using the word "author"), call recommend_books_by_author
        matched_authors = extract_authors_from_message(user_message)
        if matched_authors:
            return recommend_books_by_author(user_message)
        
        # Case 4: If no genre or author is specified, give a generic book recommendation
        response =  "I recommend you specify a genre or an author for better recommendations. You can ask for books in a specific genre like 'Fiction', 'Mystery', or 'Romance', or mention an author by name."

        return response

    # Case 2 (Alternative) - When the user mentions only the genre (no recommendation keywords)
    elif match_genre(user_message):
        # If only a genre is mentioned (without a recommendation keyword), suggest books for that genre
        return recommend_books_by_genre(user_message)

    # If no genre, author, or recommendation keyword is detected, provide a default message
    return "I'm sorry, I didn't quite understand your request. Can you please rephrase it as a book recommendation request?"




from .data.keywords import info_keywords

def extract_book_or_author_name(user_message):
    """
    Extracts book or author names from the user message. Looks for specific words 
    and tries to find matches in the authors or books data.
    """
    user_message = user_message.lower()
    print(user_message)

    # Check for book info by searching book titles in books_data
    for book in books_data:
        book_title = book['title'].lower()
        if book_title.lower() in user_message:
            return "book", book_title  # Return the type ("book") and the title
        print("book", book_title)

    # Check for author info by searching author names in authors_data
    for author_name in authors_data:
        if author_name.lower() in user_message:
            return "author", author_name  # Return the type ("author") and the name
    
    return None, None  # No match found


def display_info(user_message):
    """
    Displays information based on whether the user is asking for author info or book info.
    """
    # Check if the message contains info-related keywords
    if any(keyword in user_message.lower() for keyword in info_keywords):
        # Extract the type (author/book) and the name
        entity_type, entity_name = extract_book_or_author_name(user_message)
        
        if entity_type == "author":
            # Case 1: Author info requested
            if entity_name in authors_data:
                author_data = authors_data[entity_name]
                # Format the author information response
                response = f"**{entity_name}**\n"
                response += f"Bio: {author_data['bio']}\n"
                response += f"Notable Works: {', '.join(author_data['notable_works'])}\n"
                return response
            else:
                return f"Sorry, I couldn't find any information for the author: {entity_name}."
        
        elif entity_type == "book":
            # Case 2: Book info requested
            book_found = False
            for book in books_data:
                if book['title'].lower() == entity_name.lower():  # Case-insensitive comparison
                    book_data = book
                    response = f"**{book_data['title']}**\n"
                    response += f"Author: {book_data['author']}\n"
                    response += f"Description: {book_data['description']}\n"
                    response += f"Genre: {book_data['genre']}\n"
                    book_found = True
                    return response
            
            if not book_found:
                return f"Sorry, I couldn't find any information for the book: {entity_name}."
        
        else:
            return "Sorry, I couldn't recognize what you were asking for. Please mention either an author or book."
    
    # If the user message doesn't contain "info" keyword
    return "I'm sorry, I only respond to requests for information on books or authors. Please specify what you want info about."



from collections import Counter
from .data.keywords import trending_keywords 


def get_trending_books():
    """
    Fetches the top 5 trending books based on order frequency.
    """
    # Get all orders and extract the product (book) from each order
    orders = Order.objects.filter(status='Delivered')  # Only consider delivered orders
    books = [order.product for order in orders]
    
    # Count the frequency of each book being ordered
    book_counter = Counter(books)
    
    # Get the top 5 most ordered books
    trending_books = book_counter.most_common(5)
    
    # Prepare the response with book names and authors
    response = "Here are the top 5 trending books based on recent orders:\n"
    for book, count in trending_books:
        response += f"- {book.name} by {book.author} (Ordered {count} times)\n"
    
    return response

def handle_trending_books_request(user_message):
    """
    Handles the user's request for trending books.
    """
    # Check if the message contains any of the trending-related keywords
    if any(keyword in user_message.lower() for keyword in trending_keywords):
        # If the message is asking for trending books, get the top trending books
        return get_trending_books()
    
    # If the message does not contain any trending-related keywords
    return "Sorry, I couldn't understand your request for trending books. Please mention keywords like 'trending', 'popular', etc."

def get_response(user_message):
    """
    This function processes the user's message and routes it to the corresponding function based on the content.
    """
    
    # Lowercase the user message for easier matching
    user_message_lower = user_message.lower()

    # Case 1: Book Recommendation Request (including when only a genre is specified)
    if any(keyword in user_message_lower for keyword in recommendation_keywords["recommendation"]):
        # Check if the user has mentioned a genre
        user_genre = match_genre(user_message)
        if user_genre:
            # If a genre is found, return recommendations based on genre
            return handle_book_recommendation_request(user_message)

        # Check if the user has mentioned an author
        user_author = extract_authors_from_message(user_message)
        if user_author:
            # If an author is found, return recommendations based on author
            return handle_book_recommendation_request(user_message)
        
        # If no genre or author are specified, ask the user to provide one
        return "Please specify a genre or an author for book recommendations."
    
    # Case 2: Genre Mention Without Recommendation Keyword (like just 'fiction')
    elif match_genre(user_message):
        # If only a genre is mentioned, suggest books for that genre
        return handle_book_recommendation_request(user_message)
    
    # Case 3: Author/Book Info Request
    elif any(keyword in user_message_lower for keyword in info_keywords):
        return display_info(user_message)
    
    # Case 4: Trending Books Request
    elif any(keyword in user_message_lower for keyword in trending_keywords):
        return handle_trending_books_request(user_message)
    
    # Default response if no condition is met
    return "I'm sorry, I didn't quite understand your request. Could you please rephrase it?"



def chatbot_view(request):
    """
    Handles the chatbot interaction, receives user message, processes it, and displays the response.
    """
    if request.method == 'POST':
        user_message = request.POST.get('user_message')  # Get user input from the form
        bot_response = get_response(user_message)  # Get the bot's response using the get_response function
        
        # Save the conversation history
        chat_history = request.session.get('chat_history', [])
        chat_history.append({'user': True, 'text': user_message})  # User's message
        chat_history.append({'user': False, 'text': bot_response})  # Bot's response
        
        # Update the session with new chat history
        request.session['chat_history'] = chat_history
        
        return render(request, 'chatbot.html', {'chat_history': chat_history})  # Render the chat page with chat history
    
    # Initial page load (if it's a GET request)
    chat_history = request.session.get('chat_history', [])
    return render(request, 'chatbot.html', {'chat_history': chat_history})


def clear_chat(request):
    if request.method == 'POST':
        request.session['chat_history'] = []
    return redirect('chatbot')  # replace 'chatbot' with your chatbot view name if different
