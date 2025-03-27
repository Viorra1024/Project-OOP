from .logic import Student, Pupil
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import Book, Student, Pupil
from .models import Student as StudentModel
from .logic import Student as LogicStudent, Pupil as LogicPupil


def home(request):
    return render(request, 'library/home.html')


def register_user(request):
    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        user_id = request.POST.get('user_id')
        name = request.POST.get('name')
        surname = request.POST.get('surname')
        group = request.POST.get('group')

        # Validate user_id
        if len(user_id) != 5 or not user_id.isdigit():
            messages.error(request, "ID must be exactly 5 digits long.")
            return render(request, 'library/register_user.html')

        # Check if ID starts with 1 or 2
        if not (user_id.startswith('1') or user_id.startswith('2')):
            messages.error(request, "ID must start with 1 (Pupil) or 2 (Student).")
            return render(request, 'library/register_user.html')

        # Convert user_id to integer after validation
        user_id = int(user_id)

        try:
            if user_type == 'student':
                if not str(user_id).startswith('2'):
                    raise ValueError("Student ID must start with 2.")
                Student.objects.create(
                    id=user_id,
                    name=name,
                    surname=surname,
                    group=group
                )
                messages.success(request, f"Student {name} registered!")

            elif user_type == 'pupil':
                if not str(user_id).startswith('1'):
                    raise ValueError("Pupil ID must start with 1.")
                age = int(request.POST.get('age'))
                if age < 7:
                    raise ValueError("Pupil must be at least 7 years old.")
                Pupil.objects.create(
                    id=user_id,
                    name=name,
                    surname=surname,
                    group=group,
                    age=age
                )
                messages.success(request, f"Pupil {name} registered!")

            else:
                raise ValueError("Invalid user type selected.")

        except Exception as e:
            messages.error(request, str(e))

    return render(request, 'library/register_user.html')


def add_book(request):
    if request.method == 'POST':
        title = request.POST['title']
        author = request.POST['author']
        isbn = request.POST['isbn']
        year = request.POST['year']
        quantity = request.POST['quantity']
        label = request.POST['label']

        Book.objects.create(
            title=title,
            author=author,
            isbn=isbn,
            year=year,
            quantity=quantity,
            label=label
        )
        return redirect('all_books')

    return render(request, 'library/add_book.html')


def add_student(request):
    if request.method == 'POST':
        name = request.POST['name']
        surname = request.POST['surname']
        group = request.POST['group']
        Student.objects.create(name=name, surname=surname, group=group)
        return redirect('all_students')
    return render(request, 'library/add_student.html')


def assign_book(request):
    students = Student.objects.all()
    pupils = Pupil.objects.all()
    books = Book.objects.all()
    error = None
    success = None

    if request.method == 'POST':
        user_id = int(request.POST['student'])
        book_id = int(request.POST['book'])
        age = request.POST.get('age')

        book = Book.objects.get(id=book_id)
        student_model = Student.objects.filter(id=user_id).first()
        pupil_model = Pupil.objects.filter(id=user_id).first()

        try:
            if book.quantity <= 0:
                raise ValueError("No copies available.")

            if str(user_id).startswith('2') and student_model:
                # Logic-layer student
                user = LogicStudent(
                    user_id=student_model.id,
                    name=student_model.name,
                    surname=student_model.surname,
                    group=student_model.group
                )

                if not user.can_borrow(book):
                    raise ValueError("Student is not allowed to borrow this book.")

                student_model.borrowed_books.add(book)

            elif str(user_id).startswith('1') and pupil_model:
                if not age:
                    raise ValueError("Age is required for pupils.")
                if int(age) < 7:
                    raise ValueError("Pupil must be at least 7 years old.")

                # Logic-layer pupil
                user = LogicPupil(
                    user_id=pupil_model.id,
                    name=pupil_model.name,
                    surname=pupil_model.surname,
                    group=pupil_model.group,
                    age=int(age)
                )

                if not user.can_borrow(book):
                    raise ValueError("Pupil can only borrow books labeled 'for children'.")

                pupil_model.borrowed_books.add(book)

            else:
                raise ValueError("Invalid user ID or user not found.")

            book.quantity -= 1
            book.save()
            success = f"{user.name} borrowed '{book.title}'"

        except Exception as e:
            error = str(e)

    return render(request, 'library/assign_book.html', {
        'students': students,
        'pupils': pupils,
        'books': books,
        'error': error,
        'success': success
    })


def return_book(request):
    students = Student.objects.all()
    pupils = Pupil.objects.all()
    books = Book.objects.all()

    if request.method == 'POST':
        user_id = int(request.POST['user_id'])
        book_id = int(request.POST['book'])

        student = Student.objects.filter(id=user_id).first()
        pupil = Pupil.objects.filter(id=user_id).first()
        book = Book.objects.get(id=book_id)

        if student and book in student.borrowed_books.all():
            student.borrowed_books.remove(book)
            book.quantity += 1
            book.save()
            return redirect('student_detail', student_id=student.id)

        elif pupil and book in pupil.borrowed_books.all():
            pupil.borrowed_books.remove(book)
            book.quantity += 1
            book.save()
            return redirect('home')

    return render(request, 'library/return_book.html', {
        'students': students,
        'pupils': pupils,
        'books': books
    })


def all_books(request):
    books = Book.objects.all()
    return render(request, 'library/all_books.html', {'books': books})


def all_students(request):
    students = Student.objects.all()
    return render(request, 'library/all_students.html', {'students': students})


def student_detail(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    return render(request, 'library/student_detail.html', {'student': student})


def check_user_type(request):
    user_type = None
    error = None

    if request.method == 'POST':
        try:
            user_id = int(request.POST.get('user_id'))

            if 10000 <= user_id <= 19999:
                # Pupil ID
                user = Pupil(id=user_id, name='Dummy', surname='User', group='Group', age=10)
                user_type = user.user_type()
            elif 20000 <= user_id <= 29999:
                # Student ID
                user = Student(id=user_id, name='Dummy', surname='User', group='Group')
                user_type = user.user_type()
            else:
                raise ValueError("Invalid user ID: must start with 1 or 2 and be 5 digits.")

        except Exception as e:
            error = str(e)

    return render(request, 'library/check_user_type.html', {
        'user_type': user_type,
        'error': error
    })


def all_users(request):
    students = Student.objects.all()
    pupils = Pupil.objects.all()
    return render(request, 'library/all_users.html', {
        'students': students,
        'pupils': pupils
    })
