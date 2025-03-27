from django.db import models


class Book(models.Model):
    LABEL_CHOICES = [
        ('children', 'For Children'),
        ('general', 'General'),
    ]

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=20, unique=True)
    year = models.IntegerField()
    quantity = models.IntegerField()
    label = models.CharField(max_length=20, choices=LABEL_CHOICES, default='general')

    def __str__(self):
        return self.title


class UserBase(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    group = models.CharField(max_length=50)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.name} {self.surname} ({self.group})"


class Student(UserBase):
    borrowed_books = models.ManyToManyField(Book, blank=True)

    def user_type(self):
        return "This is a student"


class Pupil(UserBase):
    age = models.IntegerField()
    borrowed_books = models.ManyToManyField(Book, blank=True)

    def user_type(self):
        return "This is a pupil"
