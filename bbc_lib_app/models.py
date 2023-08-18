from django.db import models
from django.contrib.auth.models import AbstractUser
import os
from django.utils import timezone
from django.contrib.auth import get_user_model
import os
from django.conf import settings

class LibraryUser(AbstractUser):
    name = models.CharField(max_length=255, null=True)
    username = models.CharField(max_length=255, unique=True)
    address = models.CharField(max_length=500)
    email = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    profile_image = models.CharField(max_length=255, null=True, blank=True)
    qr_code_image = models.CharField(max_length=255, null=True, blank=True)
    badges = models.PositiveIntegerField(default=0)


class Book(models.Model):
    book_id = models.AutoField(primary_key=True, null=False)
    book_cover = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    category = models.CharField(max_length=255, null=True, blank=True)
    description = models.CharField(max_length=1500, null=True, blank=True)
    publication_date = models.CharField(max_length=255)
    isbn = models.CharField(max_length=255)
    availability_status = models.CharField(max_length=255)

    def __str__(self):
        return self.title
    
    def average_rating(self):
        ratings = Rating.objects.filter(book=self)
        if ratings.exists():
            total_ratings = ratings.aggregate(total=models.Sum('rating'))['total']
            num_ratings = ratings.count()
            return total_ratings / num_ratings
        return 0
    
    def num_ratings_by_star(self):
        ratings = Rating.objects.filter(book=self)
        rating_counts = {i: ratings.filter(rating=i).count() for i in range(1, 6)}
        return rating_counts


    def num_reviews(self):
        return Rating.objects.filter(book=self).count()
    

class Rating(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])
    review = models.TextField()

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"
    



class BorrowBook(models.Model):
    borrow_id = models.AutoField(primary_key=True)
    borrower = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrow_date = models.DateField(default=timezone.now)
    due_date = models.DateField()

    def __str__(self):
        return f"{self.borrower.username} borrowed {self.book.title}"

class Reservations(models.Model):
    user = models.ForeignKey(LibraryUser, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    reservation_date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"

class Wishlist(models.Model):
    username = models.CharField(max_length=100)
    book = models.ForeignKey('Book', on_delete=models.CASCADE)  # Assuming you have a Book model defined

    def __str__(self):
        return self.book.title