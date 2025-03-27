from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_user, name='register_user'),
    path('add-book/', views.add_book, name='add_book'),
    path('check-user/', views.check_user_type, name='check_user_type'),
    path('add-student/', views.add_student, name='add_student'),
    path('assign-book/', views.assign_book, name='assign_book'),
    path('return-book/', views.return_book, name='return_book'),
    path('users/', views.all_users, name='all_users'),
    path('students/', views.all_students, name='all_students'),
    path('books/', views.all_books, name='all_books'),
    path('student/<int:student_id>/', views.student_detail, name='student_detail'),
]
