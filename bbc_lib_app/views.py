from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib import auth
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from .models import LibraryUser, Book, Wishlist,  BorrowBook, Reservations, Rating
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
import  os
import qrcode
from pyzbar.pyzbar import decode
from django.db.models import F
from django.views.decorators.csrf import csrf_exempt
import json
from django.db.models import Q  # Add this import
from django.views.generic import RedirectView


# Create your views here.
# def context_data(request):
#     fullpath = request.get_full_path()
#     abs_uri = request.build_absolute_uri()
#     abs_uri = abs_uri.split(fullpath)[0]
#     context = {
#         'system_host' : abs_uri,
#         'page_heading' : '',
#         'page_title' : '',
#         'system_name' : 'Baptists for Africa Library System',
        
#     }

#     return context
    


def book_search(request, query):
    books = Book.objects.filter(
        Q(title__icontains=query) | Q(author__icontains=query)
    )
    return books

def index(request):
    books = Book.objects.all()

    if request.method == 'POST':
            query = request.POST['query']
            books = book_search(request, query)
    else:
            books = Book.objects.all()
    

    context = {
        'books': books,      
    }
    return render(request, 'index.html', context)

# @login_required
def home(request):
    # Retrieve any necessary data from the database

    # Perform your logic to determine if the user is logged in
    is_logged_in = request.session.get('username') is not None

    context = {
        'is_logged_in': is_logged_in,
        # Add other data you want to pass to the template
    }

    return render(request, 'home.html', context)



def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        name = request.POST['name']
        address = request.POST['address']
        email = request.POST['email']
        phone_number = request.POST['phone_number']
        role = request.POST['role']
        
        # Create a LibraryUser instance
        user = LibraryUser(
            username=username,
            password=make_password(password),
            name=name,
            address=address,
            email=email,
            phone_number=phone_number,
            role=role
        )
        
        # Save the user to the database
        user.save()
        user = authenticate(request, username=username, password=password)
        # Log in the user (optional)
        login(request, user)
        


        # Redirect to a success page
        return redirect('home')
    
    return render(request, 'signup.html')


def user_login(request):
    if request.method == 'POST':
        # Process the login form data and authenticate the user
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            else:
                return redirect('home')  # Replace 'home' with the URL name of your default page
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('user_login')

    else:
        # Render the login form
        return render(request, 'login.html')

def available_books(request):
    if 'username' in request.session:
        books = Book.objects.filter(status='available')
        return render(request, 'available_books.html', {'books': books})
    else:
        return redirect('user_login')  # Replace 'login' with your login URL name


def book_details(request, book_id):
        books = Book.objects.all()
        book = Book.objects.get(pk=book_id)
    
        # Retrieve ratings and reviews for the book
        ratings = Rating.objects.filter(book=book)

        books = get_object_or_404(Book, book_id=book_id)
        context = {
            'page_heading' : 'Book Details',
            'page_title' : 'Book Details',
            'div_style': 'row',
            'system_name' : 'Baptists for Africa Library System',
            'book': books,
            'book': book,
            'ratings': ratings,
        }
        return render(request, 'Admin/book_details.html', context)
 

def submit_review(request, book_id):
    if request.method == 'POST':
        rating_value = request.POST.get('rating')
        review_text = request.POST.get('reviewtext')
        user = request.user  # Assuming you have authentication implemented
    
        book = Book.objects.get(book_id=book_id)

        Rating.objects.create(user=user, book=book, rating=rating_value, review=review_text)

    return redirect('book_detail', book_id=book_id)


def borrow_book(request, book_id):
    if request.method == 'POST':
        # Get the book object
        book = Book.objects.get(book_id=book_id)

        # Calculate the due date (e.g., 14 days from today)
        due_date = timezone.now() + timezone.timedelta(days=14)

        # Create a BorrowBook instance for the user
        borrow_book = BorrowBook.objects.create(
            borrower=request.user,  # Assuming the user is logged in
            book=book,
            due_date=due_date,
        )

        # Update the book's availability status to "Unavailable"
        book.availability_status = "Unavailable"
        book.save()

        return redirect('user_dashboard')  # Replace 'user_dashboard' with the URL name for the user dashboard
    else:
        # Handle GET request, if needed
        pass


def borrowed_books(request):
    borrowed_books = BorrowBook.objects.all()
    context = {
            'page_heading' : 'Borrowed Books',
            'page_title' : 'Borrowed Books',
            'div_style': 'row',
            'system_name' : 'Baptists for Africa Library System',
            'borrowed_books': borrowed_books
        }

    return render(request, 'Admin/borrowedbooks.html', context)


def books(request):
    books = Book.objects.all()
    context = {
            'page_heading' : 'Manage Books',
            'page_title' : 'Manage Books',
            'div_style': 'row',
            'system_name' : 'Baptists for Africa Library System',
            'books': books,
            'book': books
    }
    return render(request, 'Admin/books.html', context)

def reserve_book(request, book_id):
    if request.method == 'POST':
        # Get the book object
        book = Book.objects.get(pk=book_id)

        # Create a Reservation instance for the user
        reservation = Reservations.objects.create(
            user=request.user,  # Assuming the user is logged in
            book=book,
            reservation_date=timezone.now(),
        )

        return redirect('user_dashboard')  # Replace 'user_dashboard' with the URL name for the user dashboard
    else:
        # Handle GET request, if needed
        pass



@login_required
def return_book(request):

    # Check if the book title is valid
    
    if not request.POST.get('book_id'):
        error = "Please enter a book ID"
        return render(request, 'Admin/returnbook.html', {'error' : "Please enter a book ID"})

    book_borrower = request.POST.get('borrower') 
    book_id = request.POST.get('book_id')
    book = Book.objects.get(book_id=book_id)

    # Check if the book is borrowed by the current user
    borrow_book = BorrowBook.objects.filter(borrower=book_borrower, book=book).first()
    if not borrow_book:
        error = 'This book is not borrowed by you.'
        return render(request, 'Admin/returnbook.html', {'error' :'This book is not borrowed by you.'})

    # Update the book status to available
    borrow_book.delete()
    book.availability_status = 'available'
    book.save()

    # Calculate the number of books returned by the user
    books_returned = BorrowBook.objects.filter(borrower=book_borrower).count()

    # Update user's badges based on the number of books returned
    if books_returned == 1:
        request.user.badges += 1
    elif 2 <= books_returned <= 3:
        request.user.badges += 2
    elif 4 <= books_returned <= 5:
        request.user.badges += 3
    elif 6 <= books_returned <= 10:
        request.user.badges += 4
    elif books_returned > 10:
        request.user.badges += 5

    request.user.save()

    return redirect('books')

def reservations(request):
    reservations = Reservations.objects.all()
    context = {
            'page_heading' : 'Manage Reservations',
            'page_title' : 'Manage Reservations',
            'div_style': 'row',
            'system_name' : 'Baptists for Africa Library System',
            'reservations': reservations
        }
    return render(request, 'Admin/reservations.html', context)

def add_book(request):
    if request.method == 'POST':
        title = request.POST['title']
        author = request.POST['author']
        publication_date = request.POST['publication_date']
        isbn = request.POST['isbn']
        category = request.POST['category']
        description = request.POST['description']
        availability_status = request.POST['availability_status']
        # Handle the book cover upload
        book_cover_image = request.FILES.get('book_cover')
        # Define the file path to save the image
        filename =   title.replace(' ', '_')  # Include the username in the file name
        new_filename = f'{filename}.jpg'
        image_path = os.path.join('bbc_lib_app/static/book_covers/', new_filename)

        
        # Read the content of the uploaded file and write it to the destination file
        with open(image_path, 'wb') as f:
            for chunk in book_cover_image.chunks():
                f.write(chunk)

        book_cover = new_filename
        book = Book.objects.create(
            title=title,
            author=author,
            book_cover=book_cover,
            publication_date=publication_date,
            isbn=isbn,
            category=category,
            description=description,
            availability_status=availability_status

        )
        # Save the user to the database
        book.save()
        return redirect('books')
    
    context = {
            'page_heading' : 'Add Book',
            'page_title' : 'Add Book',
            'div_style': 'row',
            'system_name' : 'Baptists for Africa Library System',
                  
    }
    return render(request, 'Admin/addbook.html', context)

def add_borrow(request, book_id):
    if request.method == 'POST':
        borrower_username = request.POST['borrower']
        book_title = request.POST['book']
        borrow_date = request.POST['borrow_date']
        due_date = request.POST['due_date']
        book = Book.objects.get(book_id=book_id)
        # Get the LibraryUser instance corresponding to the borrower's username
        borrower = get_object_or_404(LibraryUser, username=borrower_username)
        book=get_object_or_404(Book, title=book_title)
        borrow = BorrowBook(
            borrower=borrower,
            book=book,
            borrow_date=borrow_date,
            due_date=due_date
        )

        # Update the book's availability status to "Unavailable"
        book.availability_status = "Unavailable"
        book.save()
        
        borrow.save()

        print("Book Title:", book_title)
        return redirect('borrowed_books')

    context = {
            'page_heading' : 'Add Borrow',
            'page_title' : 'Add Borrow',
            'div_style': 'row',
            'system_name' : 'Baptists for Africa Library System',
                  
    }

    return render(request, 'Admin/addborrow.html', context)

def add_reservation(request):
    if request.method == 'POST':
        user = request.POST['user']
        book = request.POST['book']
        reservation_date = request.POST['reservation_date']

        reservation = Reservations.objects.create(
            user=user,
            book=book,
            reservation_date=reservation_date
        )

        return redirect('reservations')

    return render(request, 'Admin/reservations.html')


def searchbook(request):
        
            users = LibraryUser.objects.all()
            books = Book.objects.all()
            borrows = BorrowBook.objects.count()
            reservations = Reservations.objects.count()
            transactions = BorrowBook.objects.count()
            users_count = LibraryUser.objects.count()
            query = request.GET.get('q')
            results = []
            

            if request.method == 'POST':
                    query = request.POST['query']
                    books = book_search(request, query)
            else:
                    books = Book.objects.all()
                    
            context = {
            'users_count': users_count,
            'books': books,
            'reservations': reservations,
            'borrows': borrows,
            'transactions': transactions,
            'page_heading' : 'Book Search',
            'page_title' : 'Book Search',
            'div_style': 'row',
            'system_name' : 'Baptists for Africa Library System',
            'users': users,
            'query': query,
            'results': results,
            
            }
           
            return render(request, 'Admin/searchbook.html', context)
        
@login_required
def profile_view(request):
    users = LibraryUser.objects.all()
    context = {
            'page_heading' : 'Profile',
            'page_title' : 'Profile',
            'div_style': 'row',
            'system_name' : 'Baptists for Africa Library System',
            'users': users
        }
    
    return render(request, 'Admin/profile.html', context)

def dashboard(request):
    user = request.user
    return render(request, 'Admin/dashboard.html', {'user': user})

def user_logout(request):
    logout(request)
    return redirect('user_login')

def admin_logout(request):
    logout(request)
    return redirect('admin_login')

def admin_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.role == 'Admin':
                login(request, user)
                return redirect('admin_dashboard')  # Redirect to admin dashboard
            else:
                messages.error(request, 'You do not have admin privileges.')
                return redirect('admin_login')  # Redirect back to login page with error message
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('admin_login')  # Redirect back to login page with error message
    else:
        return render(request, 'Admin/adminlogin.html')

@login_required
def admin_dashboard(request):
    # Check if the user is logged in and has admin privileges
    if request.user.is_authenticated and request.user.role == 'Admin':
        # Get all users and books from the database
        users = LibraryUser.objects.all()
        books = Book.objects.all()

        book_count = Book.objects.count()
        borrows = BorrowBook.objects.count()
        reservations = Reservations.objects.count()
        transactions = BorrowBook.objects.count()
        users_count = LibraryUser.objects.count()


        context = {
            'users_count': users_count,
            'books': books,
            'book_count': book_count,
            'reservations': reservations,
            'borrows': borrows,
            'transactions': transactions,
            'page_heading' : 'Dashboard',
            'page_title' : 'Admin Dashboard',
            'div_style': 'row',
            'system_name' : 'Baptists for Africa Library System',
            'users': users
        }

        return render(request, 'Admin/dashboard.html', context)
    else:
        return redirect('admin_login')  # Redirect to the admin login page if not logged in or not an admin




@login_required
def edit_user(request, user_id):
    user_edit = get_object_or_404(LibraryUser, id=user_id)
    
    if request.method == 'POST':
        user_edit.user_id = request.POST.get('id')
        user_edit.name = request.POST.get('name')
        user_edit.username = request.POST.get('username')
        user_edit.address = request.POST.get('address')
        user_edit.email = request.POST.get('email')
        user_edit.phone_number = request.POST.get('phone_number')
        user_edit.role = request.POST.get('role')
        user_edit.profile_image = request.POST.get('user_profile')
        user_edit.save()
        return redirect('admin_dashboard')  # Redirect to the user list page after editing
    return ('Admin/dashboard.html', {'user_edit': user_edit})

def edit_book(request, book_id):
    book_edit = get_object_or_404(Book, book_id=book_id)
    
    if request.method == 'POST':
        book_edit.title = request.POST['title']
        book_edit.author = request.POST['author']
        book_edit.publication_date = request.POST['publication_date']
        book_edit.isbn = request.POST['isbn']
        book_edit.category = request.POST['category']
        book_edit.description = request.POST['description']
        book_edit.availability_status = request.POST['availability_status']
        # Handle the book cover upload
        book_edit.book_cover_image = request.FILES.get('book_cover')
        # Define the file path to save the image
        filename =   book_edit.title.replace(' ', '_')  # Include the username in the file name
        new_filename = f'{filename}.jpg'
        image_path = os.path.join('bfa_lib_app/static/book_covers', new_filename)

        
        # Read the content of the uploaded file and write it to the destination file
        with open(image_path, 'wb') as f:
            for chunk in book_edit.book_cover_image.chunks():
                f.write(chunk)

        book_edit.book_cover = new_filename
        book_edit.save()
        return redirect('books')  # Redirect to the user list page after editing
    return ('Admin/books.html', {'book_edit': book_edit})

@login_required
def edit_borrow(request, borrow_id):
    borrow = get_object_or_404(BorrowBook, id=borrow_id)
    if request.method == "POST":
        borrow.borrow_date = request.POST["borrow_date"]
        borrow.due_date = request.POST["due_date"]
        borrow.save()
        return redirect("borrowed_books")
    else:
        return render(request, "Admin/dashboard.html", {"borrow": borrow })
    
@login_required
def manage_user(request):
    # Check if the user is logged in and has admin privileges
    if request.user.is_authenticated and request.user.role == 'Admin':
        # Get all users and books from the database
        users = LibraryUser.objects.all()

        context = {
            'page_heading' : 'Manage Users',
            'page_title' : 'Manage Users',
            'div_style': 'row',
            'system_name' : 'Baptists for Africa Library System',
            'users': users,
            'user': users
        }

        return render(request, 'Admin/managerusers.html', context)
    else:
        return redirect('admin_login')  # Redirect to the admin login page if not logged in or not an admin

@login_required
def delete_user(request, user_id):
    user = get_object_or_404(LibraryUser, id=user_id)
    users = LibraryUser.objects.all()
    if request.method == 'POST':
        user.delete()
        return redirect('manage_user')

    return render(request, 'Admin/managerusers.html', {'users', users}, {'user': user })



@login_required
def create_user(request):
    if request.method == 'POST':
        # Process the form data and create a new user
        username = request.POST.get('username')
        password = request.POST.get('password')
        name = request.POST.get('name')
        address = request.POST.get('address')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        role = request.POST.get('role')
        user_profile_image  = request.FILES.get('user_profile')
        # Define the file path to save the image
        filename =   username.replace(' ', '_')  # Include the username in the file name
        new_filename = f'{filename}.jpg'
        image_path = os.path.join('bbc_lib_app/static/profile_images', new_filename)

        
        # Read the content of the uploaded file and write it to the destination file
        with open(image_path, 'wb') as f:
            for chunk in user_profile_image.chunks():
                f.write(chunk)

        user_profile=filename
        # Create a LibraryUser instance
        user = LibraryUser(
            username=username,
            password=make_password(password),
            name=name,
            address=address,
            email=email,
            phone_number=phone_number,
            role=role,
            profile_image=user_profile
        
        )
        
        # Save the user to the database
        user.save()
        
        # Optionally, perform any additional actions or redirect to a different page
        return redirect('manage_user')  # Redirect to the user list page after creating the user
    
    context = {
            'page_heading' : 'Add User',
            'page_title' : 'Add User',
            'div_style': 'row',
            'system_name' : 'Baptists for Africa Library System',
                  
    }
    return render(request, 'Admin/adduser.html', context)


@login_required
def user_qr(request, user_id):
    user = get_object_or_404(LibraryUser, id=user_id)
    
    # Generate the URL for the user profile using reverse URL lookup
    url = request.build_absolute_uri(reverse('user_view', args=[user.id]))
    
    # Generate the QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # Create an image from the QR code
    qr_image = qr.make_image(fill_color="black", back_color="white")
    filename = f'{user.username}_qrcode.jpg'
    image_path = os.path.join('bbc_lib_app/static/user_qrcodes', filename)
    qr_image.save(image_path)
    
    user.qr_code_image = filename
    user.save()
    
    context = {
        'user': user,
        'qr_image_data': filename,  # Pass the filename instead of qr_image
    }
    return render(request, 'Admin/profile.html', context)

def page_search(request):

    if request.method == 'POST':
            query = request.POST['query']
            page_detail = query
            url = reverse(page_detail)
            
    return RedirectView(url)

def search_users(request, query):
    users = LibraryUser.objects.filter(
        Q(name__icontains=query) | Q(username__icontains=query)
    )
    return users


def user_profiles(request):
    # Check if the user is logged in and has admin privileges
    if request.user.is_authenticated and request.user.role == 'Admin':
        # Get all users and books from the database
        if request.method == 'POST':
            query = request.POST['query']
            users = search_users(request, query)
        else:
            users = LibraryUser.objects.all()

        books = Book.objects.count()
        borrows = BorrowBook.objects.count()
        reservations = Reservations.objects.count()
        transactions = BorrowBook.objects.count()
        users_count = LibraryUser.objects.count()

        # Get the selected filter
        filter_group = request.GET.get('filter_group')

        # Filter the users based on the selected filter
        if filter_group == 'all':
            users = users
        elif filter_group == 'Admins':
            users = users.filter(role='Admin')

        context = {
            'users_count': users_count,
            'books': books,
            'reservations': reservations,
            'borrows': borrows,
            'transactions': transactions,
            'page_heading' : 'User Profiles',
            'page_title' : 'User Profiles',
            'div_style': 'row',
            'system_name' : 'Baptists for Africa Library System',
            'users': users
        }

        return render(request, 'Admin/user_profiles.html', context)
    else:
        return redirect('admin_login')  # Redirect to the admin login page if not logged in or not an admin
    
def user_profile_view(request, user_id):
    users = get_object_or_404(LibraryUser, id=user_id)
    context = {
            'page_heading' : 'Profile',
            'page_title' : 'Profile',
            'div_style': 'row',
            'system_name' : 'Baptists for Africa Library System',
            'user': users
        }
    

    return render(request, 'Admin/user_view.html', context)

@csrf_exempt  # Disabling CSRF protection for simplicity. Ensure proper CSRF handling in production.
def process_qr_code_scan(request):
    if request.method == 'POST':
        data = json.loads(request.body)['data']
        # Process the QR code data here
        response_data = {'message': f'QR code data received: {data}'}
        return JsonResponse(response_data)
    


def book_detail(request, book_id):
    book = Book.objects.get(pk=book_id)
    
    # Retrieve ratings and reviews for the book
    ratings = Rating.objects.filter(book=book)
    
    context = {
        'book': book,
        'ratings': ratings,
    }
    return render(request, 'book_detail.html', context)

# def custom_404_view(request, exception):
#     return render(request, 'Admin/404.html', status=404)