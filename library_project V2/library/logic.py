from .models import Book


class User:
    def __init__(self, user_id, name, surname, group, borrowed_books=None):
        if not (10000 <= user_id <= 29999):
            raise ValueError("Invalid user_id: must be 5 digits starting with 1 or 2.")
        self.user_id = user_id
        self.name = name
        self.surname = surname
        self.group = group
        self.borrowed_books = borrowed_books if borrowed_books else []

    def borrow_book(self, book: Book):
        if self.can_borrow(book):
            self.borrowed_books.append(book)
            return True
        return False

    def return_book(self, book: Book):
        if book in self.borrowed_books:
            self.borrowed_books.remove(book)
            return True
        return False

    def check(self):
        if str(self.user_id).startswith('2'):
            return "This is a student"
        elif str(self.user_id).startswith('1'):
            return "This is a pupil"
        else:
            return "Unknown user type"

    def can_borrow(self, book: Book):
        raise NotImplementedError("Subclasses must implement can_borrow method")


class Student(User):
    def can_borrow(self, book: Book):
        return True


class Pupil(User):
    def __init__(self, user_id, name, surname, group, age, borrowed_books=None):
        super().__init__(user_id, name, surname, group, borrowed_books)
        self.age = age

    def can_borrow(self, book: Book):
        if self.age < 7:
            return False
        return book.label == 'children'
